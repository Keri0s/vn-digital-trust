# Lưu evidence, snapshot và giao dịch v0.1

Ngày 2026-10-19. Đặc tả bước 05; chưa triển khai hoặc thử nghiệm lỗi/restore. Áp dụng cùng [API](api-contract-v0.1.md), [schema](schema-v0.1.sql), [mô hình dữ liệu](data-model-v0.1.md) và [cấu hình](configuration-v0.1.md). Các tên thao tác trong tài liệu này là trách nhiệm nghiệp vụ; tên bảng/cột chính thức ở schema.

## 1. Đường vật lý và điểm kiểm soát

Mọi request UI, JSON, multipart, tải evidence và export đều đi **Browser → Caddy reverse proxy/TLS → ứng dụng Django/DRF → Policy gate → module nghiệp vụ**. Proxy là điểm kết thúc TLS; kết nối tới ứng dụng chỉ trên loopback hoặc mạng riêng không được client truy cập trực tiếp. Public route chỉ có đăng nhập, CSRF bootstrap và health tối thiểu; endpoint evidence không public. Proxy chuẩn hóa Host/forwarded headers từ nguồn tin cậy; ứng dụng chỉ tin proxy đã cấu hình. Cấu hình không expose cổng DB, worker hoặc đường dẫn kho tệp.

`POST /api/v1/evidence-items/{id}/evidence-revisions` nhận `multipart/form-data` gồm metadata và đúng một file, hoặc JSON cho reference theo OpenAPI. Mũi tên nộp file ở sơ đồ kiến trúc cũ biểu diễn loại dữ liệu; triển khai phải giữ đủ reverse proxy và policy gate. [Sequence upload](upload-sequence-v0.1.svg) chỉ rõ đường này và nhánh lỗi.

Gate kiểm tra session VDT, user active, CSRF với request thay đổi trạng thái, permission, tổ chức/branch/object scope, assessment assignment và expiry. Kiểm session/route scope trước khi đọc nội dung nghiệp vụ; multipart handler phải giới hạn stream và vùng tạm ngay cả khi parser framework cần đọc body sớm. Không xem việc middleware được khai báo là bằng chứng mọi DRF view đã được bảo vệ. List queryset, create payload và nested IDs đều kiểm scope, không chỉ detail handler.

## 2. Hai loại evidence và vùng lưu

| Loại | Nội dung được lưu bất biến | Quy tắc dùng |
| --- | --- | --- |
| FILE | bytes, SHA-256 do server tính, kích thước, detected media type, source/owner/collected_at/valid_until, scope, environment/config version và redaction | Hash client chỉ là kỳ vọng để đối chiếu. Hash đúng không chứng minh provenance đúng hoặc nội dung an toàn. |
| REFERENCE | URI và mô tả nguồn được nhập, thời điểm, scope, expected digest nếu có; digest của metadata tách digest nội dung | Server không tự fetch URL/DNS/redirect. COMMITTED nghĩa là metadata reference đã lưu, không nghĩa nguồn ngoài còn tồn tại. Verifier ghi observed digest/observation; muốn tái lập bytes phải nộp FILE revision. |

Kho riêng ngoài web/static root, service account riêng, tên nội bộ sinh từ UUID; tên gốc chỉ là metadata đã escape. Không dùng path/filename do client chỉ định, không follow symlink ra khỏi root, không deduplicate xuyên phạm vi bằng digest công khai. Các vùng `quarantine/`, `objects/`, `exports/`, `backup/` có quyền riêng. Quarantine và objects cùng filesystem để đổi tên nguyên tử. Reverse proxy không `file_server` kho evidence, không phát signed/public URL bỏ qua gate.

Chính sách v0.1: mỗi upload tối đa **20 MiB**, metadata tối đa **64 KiB**, request multipart tối đa **21 MiB**; một upload đang xử lý mỗi principal, tối đa hai trên host; scanner tuần tự. Đây là giới hạn vận hành được chọn cho prototype, phải đo ở bước 06. Cho phép TXT/LOG UTF-8, JSON, CSV, PDF, PNG, JPEG theo extension + detected MIME/signature; tên mở rộng không đủ. Từ chối archive, executable, HTML/SVG và tài liệu macro; dữ liệu cần dạng khác nộp reference hoặc tạo policy version mới. Không tự giải nén/chạy/render tài liệu do người dùng nộp. CSV xuất được escape formula injection. Mọi file được quét bằng engine/signature có version trước COMMITTED; scanner thiếu/lỗi/hết thời gian thì giữ chưa sẵn sàng và trả lỗi retry được, không đánh dấu VERIFIED. Chữ ký hết hạn theo cấu hình cũng chặn commit.

Các biện pháp định dạng, giới hạn, tên nội bộ, kho ngoài webroot và quét trước xử lý dựa trên [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html); các con số trên là quyết định riêng của dự án. Django hỗ trợ upload handler và đọc theo chunk để tránh giữ toàn file trong RAM; phải cấu hình handler trước khi body được parse. [Django 5.2 — file uploads](https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/).

## 3. Upload và sự cố giữa filesystem/DB

1. Gate kiểm quyền hiện hành; kiểm header, content length nếu có, giới hạn rate/quota và Idempotency-Key. Đặt operation ID; stream vào quarantine với giới hạn byte độc lập Content-Length. Không giữ transaction/row lock trong lúc truyền hoặc quét. Chưa tạo revision nghiệp vụ khi chưa đủ bytes/hash/metadata.
2. Sau stream: kiểm checksum, metadata, MIME, scan. Canonical request hash bao gồm method/path, metadata chuẩn hóa, expected parent version và digest bytes thực. Không đưa boundary multipart ngẫu nhiên vào hash. Scan thất bại an toàn/malware khác quyết định nghiệp vụ REJECTED; scanner không có quyền tạo VerificationDecision.
3. Transaction ngắn tạo revision metadata bất biến và bản ghi storage STAGED, liên kết upload operation; kiểm quyền/scope và expected version. Chưa tăng head của EvidenceItem và chưa cho assessment dùng revision.
4. Flush/fsync file và thư mục thích hợp; đổi tên quarantine → final object cùng filesystem, không ghi đè object đã có. Ghi expected final key trước rename để có thể phục hồi sau crash. Chưa coi file ở final path là evidence sẵn sàng.
5. Transaction cuối: khóa guard quyền, principal/session và aggregate liên quan; đọc thời gian DB hiện tại; kiểm lại quyền/expiry, versions context/item/assignment và integrity; chuyển storage STAGED → COMMITTED, tăng head/version, ghi audit và kết quả idempotency cùng transaction. Chỉ sau commit trả `201` với revision ID. Revision vẫn UNVERIFIED về nghiệp vụ.

| Điểm lỗi | Dữ liệu còn lại | Phục hồi và kết quả |
| --- | --- | --- |
| Client ngắt/oversize/truncated | Upload operation + file tạm chưa hoàn tất | Bỏ file chưa hoàn tất theo lease/quota; không có evidence dùng được. 413 khi vượt giới hạn. |
| Hash khác/định dạng không cho phép/malware | Audit an toàn, quarantine bị cô lập | Không commit. Client sửa nội dung dùng key mới. Không biến lỗi nộp tệp thành control failure. |
| Scanner không sẵn sàng | Operation chưa có kết quả thành công | 503, retry cùng key/payload; không bỏ qua scan. |
| DB hỏng trước tạo STAGED | File tạm | Reconciler dọn sau thời gian grace và xác nhận không có operation đang hoạt động. |
| STAGED đã ghi, rename chưa xong | Metadata STAGED + file tạm | Không cho đọc/verify/assessment; retry có kiểm quyền lại hoặc chuyển ORPHANED. |
| Rename xong, transaction cuối rollback | File final + STAGED | Reconciler chỉ xác định/dọn orphan, không tự commit bằng quyền cũ. Người dùng retry cùng key được kiểm lại quyền/version. |
| Quyền hết hạn/thu hồi hoặc parent đổi trước commit | STAGED không dùng được | Deny hoặc conflict; bảo toàn audit, không trả bytes. Giữ/dọn orphan theo policy. |
| Commit thành công, response mất | COMMITTED + idempotency result | Retry cùng key/payload trả cùng resource sau reauthorization; không sinh revision thứ hai. |
| File mất/hỏng sau commit | Metadata lịch sử + trạng thái vật lý lỗi | Storage thành INTEGRITY_FAILED, không đổi hash/history. Download/assessment mới bị chặn; khôi phục đúng bytes từ backup có audit hoặc nộp revision mới. |

`storage_state` là trạng thái vận hành của storage record, được API trình bày trên EvidenceRevision. Revision metadata/bytes không được sửa để che lỗi. Các chuyển hợp lệ: STAGED→COMMITTED hoặc ORPHANED; COMMITTED→INTEGRITY_FAILED; INTEGRITY_FAILED→COMMITTED chỉ khi restore cùng digest/kích thước được kiểm tra và có audit; ORPHANED không được tự hồi thành COMMITTED. Lịch sử storage event lưu riêng. ORPHANED là payload không được công bố và không được snapshot tham chiếu, không là cách xóa evidence đang dùng.

## 4. Đọc, xác minh và snapshot

Download đi lại qua proxy và gate, kiểm scope/expiry ngay trước phát bytes. Chỉ dùng FILE COMMITTED với digest khớp; mở file handle an toàn rồi kiểm và phát từ cùng handle để tránh đổi path giữa kiểm và đọc. Trả attachment, `Cache-Control: private, no-store`, `X-Content-Type-Options: nosniff`; không render inline. Stream dài kiểm hủy khi permission bị thu hồi và dừng ở expiry; bytes đã phát trước đó không thu hồi được. Giới hạn kích thước giúp giới hạn thời gian xử lý nhưng không thay kiểm quyền.

VerificationDecision append-only và nhắm đúng revision + scope. `VERIFIED`/`REJECTED` là kết luận nội dung/provenance, `verification_mode` là nguồn xác minh. Không có decision phù hợp → UNVERIFIED. Hết valid_until, mất storage, sai scope, môi trường đã đổi hoặc decision không còn dùng được → không được dùng cho assessment mới dù trước đó VERIFIED. Chọn decision có thứ tự trong đúng scope/time; không chọn “mới nhất toàn cục” để mở quyền hoặc phủ nhận kết quả ở scope khác. Khi nhiều scope giao nhau chưa có quy tắc bao hàm đã kiểm, yêu cầu scope chính xác hoặc xác minh lại.

ControlAssessment đóng băng criteria/version, implementation/context, evidence revision IDs và **decision IDs cụ thể**. RiskEvaluation đóng băng input/confirmation/ranges, paths, control assessment IDs, method/profile/rubric, RM results và review facts. Report đóng băng graph IDs, giá trị context, gap/task/decision ở `as_of`; đọc report cũ không truy “latest” để thay giá trị đã chụp. Quyền xem metadata/nội dung luôn kiểm theo hiện tại; lịch sử không trở thành lối vượt quyền.

Hai mốc thời gian được tách: `effective_at/collected_at` là thời điểm sự việc được khai báo, `recorded_at` do server gán là lúc hệ thống biết. Report `as_of` chỉ chọn bản đã recorded trước hoặc bằng as_of; evidence nộp muộn không xuất hiện ngược thời gian trong báo cáo cũ. Không nhận actor/time/hash/result tính toán do client tự quyết. Canonical snapshot format có schema version và SHA-256 của biểu diễn chuẩn; dùng số nguyên R25 và chuỗi decimal ổn định, sort keys, UTF-8, UTC. Hash là kiểm tra thay đổi dữ liệu, không là chữ ký/chứng nhận chống quản trị viên DB.

## 5. Transaction, khóa và idempotency

**Ranh giới transaction:** assessment + children/inputs + decisions + audit + idempotency success được commit nguyên khối. Gap/task là thao tác tường minh riêng hoặc cùng command có danh sách yêu cầu rõ; kết quả assessment không tự đóng task. Business audit thất bại → rollback mutation. Audit denial sau rollback viết transaction riêng tối thiểu, không chứa bytes/secret/payload nhạy cảm; nếu DB audit không hoạt động thì request bị từ chối và log vận hành cục bộ tối thiểu để khôi phục, không bỏ gate.

**Race quyền:** một guard quyền cấp organization với version phù hợp một SME nhỏ. Mọi cấp/thu hồi quyền, disable user, revoke session và final commit nhạy cảm dùng cùng guard trong transaction ngắn. Do vậy thao tác thu hồi hoàn tất trước final gate luôn được final gate nhìn thấy; không chỉ tin permission cache. Kiểm `clock_timestamp()` tại final gate, không dùng `now()` cố định từ đầu transaction; `t >= expires_at` là deny. Ghi t_gate/permission version vào audit; gate cuối nằm sát commit và dùng deferred check expiry nếu transaction có nhiều ghi. Quyền thay đổi sau điểm commit áp dụng cho lần đọc/thao tác tiếp theo. Không giữ khóa trong suốt upload hoặc tải xuống.

**OCC:** update dữ liệu mutable dùng strong ETag/If-Match gắn `version`; `UPDATE ... WHERE id=? AND version=?` rồi tăng version. Không tìm thấy version → 412; thiếu điều kiện → 428. Aggregate membership, criteria/context revision và evidence decision dependencies có expected ID/version, thay đổi trước final commit → 409 DEPENDENCY_CHANGED. Nhận snapshot ID cố định không đủ để mặc nhiên dùng evidence đã hết hạn. Lock thứ tự ổn định: auth guard → aggregate ID tăng dần → dependent rows → audit/idempotency. PostgreSQL row locks giữ tới hết transaction và chặn write/lock xung đột; deadlock/serialization failure được rollback rồi retry có giới hạn. [PostgreSQL 17 — explicit locking](https://www.postgresql.org/docs/17/explicit-locking.html).

**Idempotency:** unique `(organization, principal, method, canonical_path, key)`; key UUID, canonical payload hash + expected version, result status/resource IDs, operation state/lease, time. Cùng key khác hash → 409; đang xử lý → 409 OPERATION_IN_PROGRESS với Retry-After; thành công → cùng resource sau kiểm lại quyền; lỗi tạm thời trước commit có thể retry cùng key. Multipart phải stream/hash hoặc kiểm chứng cùng bytes trước replay, không tin digest client để tuyên bố payload trùng. Bản ghi giữ suốt vòng đời hồ sơ v0.1; nếu triển khai retention sau này phải giữ tombstone key/hash/resource để key cũ không tạo quyết định mới. Replay response không lưu blob hoặc nội dung nhạy cảm không còn được phép đọc.

**If-Match và idempotency là hai kiểm tra khác nhau.** Replay thao tác đã thành công không cần current version vẫn bằng version cũ, nhưng phải xác thực hash và quyền hiện tại; request mới với key mới phải kiểm current version. Semantics If-Match/412 theo [RFC 9110 §13.1.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1); application Idempotency-Key là contract riêng của VDT.

## 6. Background work, export, backup

Worker tuần tự dùng durable job trong PostgreSQL, lease/attempt/deadline, xử lý lặp an toàn. Không dùng queue trong RAM làm nguồn sự thật. Export job ghi actor/scope/request hash/snapshot IDs, kiểm lại quyền khi chạy, trước công bố và mỗi download. Artifact có expiry và storage key riêng; sau expiry chỉ giữ metadata/audit. Job không được nâng quyền người yêu cầu; service account chỉ quyền thao tác kho/job. Cleanup chỉ dọn operation hết lease và file không được committed snapshot tham chiếu, có grace period, khóa và audit; retention không xóa domain history v0.1.

Chọn backup đơn giản phù hợp đồ án: maintenance mode chặn mutation/upload/job mới, chờ transaction và stream đang chạy kết thúc, chụp DB cùng manifest tất cả COMMITTED file hashes, sao chép immutable objects rồi đối chiếu manifest trước mở ghi. Giữ bản backup mã hóa và khóa tách khỏi bộ dữ liệu; không đặt backup trong webroot. Đây là thiết kế offline backup, chưa cam kết RPO/RTO. Restore vào môi trường cô lập, tắt job và chặn outbound, kiểm schema version/FKs/hash/scope, vô hiệu toàn bộ session cũ, thử quyền và mở snapshot trước khi dùng. File thiếu/hỏng phải hiện INTEGRITY_FAILED, không tự giữ trạng thái sẵn sàng. Phục hồi metadata không có blobs không được báo restore thành công.

## 7. Kiểm chứng cần thực hiện ở bước 06

Fault injection tại từng dòng bảng §3; hai upload cùng key và khác key trên một head; revoke/expiry ở đầu, giữa, sát commit và giữa download; cache quyền cũ; reference private/link-local URL không phát network request; scanner unavailable/malware/oversize; path traversal/symlink; metadata/file backup lệch; snapshot as_of với evidence nộp muộn; audit lỗi rollback; worker restart/lease expiry; restore từ manifest. Tất cả hiện **NOT_RUN**. Kết quả parse tài liệu/DDL/OpenAPI và render sơ đồ bước 05 không thay thế các kiểm thử này.
