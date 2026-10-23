# VN Digital Trust — Cấu hình và seed RBAC v0.1

**Ngày:** 2026-10-20 (Asia/Bangkok). **Phạm vi:** thiết kế bước 05; một SME, hai chi nhánh. Tệp [config-template-v0.1.json](config-template-v0.1.json) là mẫu chưa đủ điều kiện triển khai; [rbac-seed-v0.1.json](rbac-seed-v0.1.json) là phép chiếu dữ liệu giả lập có nguồn. Không có tài khoản thật, quyết định phê duyệt, kết quả CRM hoặc kết quả lab được tạo từ hai tệp này.

Tài liệu triển khai các lưu ý 3.1–3.4, [kiến trúc bước 04](../architecture/architecture-technical-v0.1.md), [fixture gốc](../planning/lab-fixtures-v0.1.json) và [bổ sung bước 03](../use-cases/flow-fixtures-v0.2.json). Công nghệ được chọn ở [technology-decisions-v0.1.md](technology-decisions-v0.1.md); API và transaction tuân theo các contract cùng thư mục.

## 1. Cách nạp và kiểm tra cấu hình

Chọn cấu hình JSON theo release, nạp một lần trước phục vụ request; biến môi trường chỉ chỉ định đường dẫn cấu hình, secret references và nhận diện môi trường. Không âm thầm gộp các giá trị mẫu CRM vào cấu hình có hiệu lực. Khóa không biết, sai kiểu, giá trị âm, origin trùng/sai định dạng hoặc trường bắt buộc còn `null` làm preflight thất bại trong phạm vi phụ thuộc tương ứng.

| Biến môi trường | Giá trị | Kiểm tra bắt buộc |
| --- | --- | --- |
| `VDT_CONFIG_PATH` | Đường tuyệt đối đến JSON cấu hình VDT của release | Tệp chỉ operator đọc/ghi, hash khớp manifest; không nằm trong evidence/public root. |
| `VDT_ENVIRONMENT_ID` | Mã môi trường riêng, ví dụ tên được operator đặt | Không rỗng; ghi vào audit/release và snapshot; không lấy từ client. |
| `VDT_DATABASE_DSN_SECRET_REF` | Tham chiếu DSN PostgreSQL | Resolve bằng quyền service account; không ghi secret vào JSON/audit/report. |
| `VDT_DJANGO_SECRET_KEY_REF` | Tham chiếu khóa Django riêng của môi trường | Resolve trước mở dịch vụ; không dùng khóa fixture hoặc khóa CRM. |
| `VDT_BACKUP_KEY_SECRET_REF` | Tham chiếu khóa mã hóa backup | Khác tài khoản ứng dụng; có quy trình phục hồi quyền operator. |

Các biến tham chiếu secret có quyền ưu tiên duy nhất đối với trường tương ứng; xung đột với JSON phải bị phát hiện và ghi cấu hình đã resolve không chứa secret. Các tham số nghiệp vụ còn lại chỉ lấy từ JSON phiên bản đã duyệt. Không cho HTTP request, query string, header hay `fixture_clock` ghi đè config hoặc thời gian server.

Ngày giờ lưu UTC có timezone; giao diện hiển thị Asia/Bangkok. Giá trị thời gian là số nguyên giây; `MiB = 1.048.576 bytes`, `KiB = 1.024 bytes`. Dùng thời gian server có đồng bộ để xét expiry; tại `now == expires_at` quyền đã hết hạn. `null` có ý nghĩa theo trường: với ngưỡng bắt buộc là chưa chốt; với cookie Domain là host-only; với expiry assignment là không thêm hạn riêng nhưng mọi hạn khác vẫn áp dụng.

Lưu bản cấu hình đã resolve, hash và người duyệt cùng release. Thay đổi config tạo revision mới, kiểm tra lại rồi mới kích hoạt; không sửa revision đã được evidence/evaluation tham chiếu. Giá trị secret không nằm trong canonical payload; chỉ lưu reference/version và hash manifest của cấu hình không chứa secret.

## 2. Xác thực VDT tách khỏi `AUTH-CRM-01`

Chọn VDT local username/password qua Django, `PBKDF2PasswordHasher` (PBKDF2-SHA256), salt ngẫu nhiên cho từng mật khẩu và work factor của bản Django đã khóa; dùng password validators. Không tự tạo mật khẩu từ username hoặc fixture, không ghi password/hash/session token vào evidence, report hoặc audit. Work factor chỉ tăng theo phép đo và chính sách, không giảm âm thầm. [Django password management](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/).

Session VDT lưu PostgreSQL, cookie `__Host-vdt_session; Secure; HttpOnly; SameSite=Lax; Path=/`, không `Domain`. Rotate session khi login và đổi mật khẩu; logout thu hồi session hiện tại; đổi/reset mật khẩu thu hồi session theo contract, vô hiệu user thì mọi session không được cấp quyền. CSRF bắt buộc với login và các request thay đổi trạng thái; cùng origin HTTPS. VDT dùng tài khoản, session, cookie, secret và namespace riêng với CRM. [Django sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/).

| Trường trong `vdt.authentication` | Kiểu/đơn vị | Trạng thái thiết kế |
| --- | --- | --- |
| `credential_method`, `password_hasher` | Enum/class cố định | `LOCAL_USERNAME_PASSWORD`; class Django đã chọn trong JSON. |
| `session_idle_timeout_seconds` | Integer > 0 | `null`, phải chọn trước phục vụ phiên; hoạt động nền tự động không kéo dài idle. |
| `session_absolute_timeout_seconds` | Integer > 0, ≥ idle timeout | `null`, tính từ thời điểm xác thực; hoạt động không gia hạn tuyệt đối. |
| `max_attempt_limit` | Integer > 0 | `null`, giới hạn thử login được duyệt cho VDT. |
| `failed_attempt_window_seconds`, `failed_attempt_lockout_seconds` | Integer > 0 | `null`, cửa sổ đếm và thời gian tạm khóa; áp dụng theo tài khoản và nguồn trong chính sách. |
| `authentication_method_policy_ref` | Reference không rỗng | `null`, tài liệu cấp tài khoản/bootstrap/reset/rate limit được operator xác nhận trước lab. |
| `mfa_runtime_claim` | Trạng thái tuyên bố | `NOT_IMPLEMENTED_OR_VERIFIED`; fixture `ENROLLED_SIMULATED` không là dữ liệu enroll thực. |

Đăng nhập thất bại trả thông báo chung; rate limit và audit không lộ mật khẩu hoặc xác nhận tài khoản tồn tại. Auth, permission, scope, assignment và expiry được kiểm trong Policy gate với trạng thái hiện hành. Không dùng cache quyền ở v0.1. Framework authentication không thay object-scope filtering của list/detail/create/export/download.

Các số `120 / 5 / 900` do người dùng nêu là ví dụ cho cấu hình CRM; chúng không được dùng làm mặc định của VDT. Phương thức local password VDT đã được chọn cho prototype; việc chấp thuận cho môi trường sử dụng thực tế nằm trong chính sách xác thực trước triển khai.

## 3. Trường cấu hình CRM và cách lưu `AuthenticationProfile`

`AUTH-CRM-01` là cấu hình của control `AC-DEMO-01` trên `AST-CRM`. Bản template giữ `status = TO_SET_BEFORE_LAB`, `implementation_status = NOT_IMPLEMENTED`, các giá trị có hiệu lực là `null`. Các ví dụ chỉ nằm trong `illustrative_examples_not_effective`; không có fallback tự động.

| Trường trong `crm_authentication_profile.effective_values` | Kiểu và ràng buộc | Ví dụ tham khảo | Điều kiện trước lab |
| --- | --- | --- | --- |
| `challenge_ttl_seconds` | Integer > 0; challenge dùng một lần, ràng buộc user/session/purpose; hết hạn tại mốc bằng TTL | `120` | Chốt với build CRM, đủ kiểm thử hết hạn và replay; snapshot giá trị. |
| `max_attempt_limit` | Integer > 0; đếm nguyên tử trong cửa sổ và mục đích đã định | `5` | Chốt đếm thất bại/bị khóa/reset; kiểm đồng thời không vượt ngưỡng. |
| `session_idle_timeout_seconds` | Integer > 0 | `900` | Chốt hoạt động nào gia hạn idle; không gia hạn bởi polling nền. |
| `rp_id` | Tên miền lowercase chuẩn hóa, không scheme/port/path; đúng domain quan hệ với origin | Không đặt mẫu | Kiểm RP ID của môi trường WebAuthn thực; không dùng IP/wildcard tùy tiện. |
| `allowed_origins` | Mảng origin HTTPS, không rỗng; scheme + host + port chuẩn hóa, không path/query/fragment/userinfo/wildcard | Không đặt mẫu | Allowlist chính xác cho CRM; không lấy từ `Origin` client để tự thêm. |

Với WebAuthn, RP ID phải thỏa quy tắc effective domain của origin trong triển khai đã chọn; validator dùng trình kiểm RP/origin của thư viện CRM được khóa, không dùng phép `endsWith` đơn giản. Cấu hình origin của VDT và CRM được xác nhận riêng. Nguồn chuẩn: [WebAuthn RP ID](https://www.w3.org/TR/webauthn-3/#rp-id), [origin validation](https://www.w3.org/TR/webauthn-3/#sctn-verifying-assertion).

Các trường bổ sung đã có tên cụ thể trong JSON để chốt các tiêu chí CE-01/TC-01:

| Nhóm | Trường | Kiểm tra |
| --- | --- | --- |
| Thử lại | `failed_attempt_window_seconds`, `failed_attempt_lockout_seconds` | Integer > 0; tách ngưỡng thử password/second factor/recovery trong policy, không bỏ giới hạn bằng thay flow. |
| Phiên/reauth/thu hồi | `session_absolute_timeout_seconds`, `reauth_max_age_seconds`, `revocation_max_delay_seconds` | Absolute ≥ idle; reauth/revocation ≥ 0, giá trị 0 có nghĩa yêu cầu ngay; định nghĩa rõ hoạt động cần reauth. |
| Enrollment/add credential | `enrollment_bootstrap_policy_ref`, `credential_addition_policy_ref` | Reference tới policy có revision; không có enrollment bằng password-only. |
| Recovery | `recovery_identity_verification_policy_ref`, `recovery_approver_role_ref`, `recovery_session_action` | Policy, người có quyền duyệt và hành động phiên phải cụ thể; không recovery bằng password-only; revoke credential cũ theo tiêu chí. |
| Notification | `notification_policy_ref`, `notification_delivery_max_seconds`, `notification_destination_ref` | Reference và thời hạn > 0, đích lab được phép; không suy ra đã gửi chỉ từ cấu hình. |

Các yếu tố cố định từ fixture được giữ: `PASSWORD + WEBAUTHN`, user verification required, không TOTP fallback, không passwordless, quyền truy cập nghiệp vụ chỉ sau cả hai yếu tố. Không suy ra hardware protection hoặc khả năng CRM từ tên công nghệ.

Thiết kế DB lưu mỗi profile dưới dạng một `authentication_profile_version` bất biến, có `code`, `revision_number`, `system_id`, `configuration_state`, các cột typed cho năm trường người dùng yêu cầu và ngưỡng phụ, policy JSON có reference/version, người/thời điểm duyệt. Cặp `(code, revision_number)` unique; version thuộc `snapshot_registry`, có canonical hash, nguồn và environment fingerprint. Trạng thái cấu hình DB là `TO_SET_BEFORE_LAB | PROPOSED | APPROVED`; approved nghĩa cấu hình đã được người có quyền duyệt, không phải control đã PASS. `APPROVED` đòi hỏi đủ trường và policy/environment liên quan; transaction service kiểm toàn bộ preflight bổ sung ngoài CHECK tối thiểu của DB.

`effective_values` trong template là cách tổ chức tệp: import ánh xạ các giá trị sang cột typed cùng tên, ánh xạ policy references vào `enrollment_policy`/`recovery_policy`/`notification_policy`, và nối đúng system CRM. Không lưu cả khối template như một field duy nhất để bỏ qua constraints. Approval từ template trống không tạo approval DB. EvidenceRevision và lần chạy kiểm thử tham chiếu chính xác profile version; sửa giá trị tạo version mới và không viết lại evidence hoặc snapshot cũ.

Canonical hash được tạo từ payload đã chuẩn hóa theo quy ước snapshot chung, trước khi gắn hash; không hash trường hash của chính nó. `canonical_config_sha256 = null` ở template nghĩa chưa có cấu hình có hiệu lực. Khi profile thay đổi, retest phải ghi khác biệt environment/input và đánh giá tương đương trước tính delta; không tự gọi hai lần chạy là so sánh hợp lệ.

## 4. TLS, upload, lưu tệp và scanner

Mọi upload theo đường `Browser → Caddy Reverse proxy/TLS → VDT auth + CSRF + Policy gate → evidence intake`. Policy gate kiểm identity/route scope trước đọc nghiệp vụ, giới hạn streaming trong khi nhận và kiểm lại permission/scope/expiry/version ngay trước commit. Proxy hoặc parser có thể nhận bytes trước kiểm domain; các bytes đó chỉ là vùng tạm và không là evidence COMMITTED.

| Tham số VDT đã chọn | Giá trị thiết kế | Áp dụng |
| --- | --- | --- |
| `max_file_bytes` | 20 MiB = 20.971.520 | Một file mỗi upload; đếm bytes thực nhận. |
| `max_metadata_bytes` | 64 KiB = 65.536 | JSON UTF-8 metadata; giới hạn trước parse. |
| `max_request_bytes` | 21 MiB = 22.020.096 | Tổng multipart gồm file, metadata, headers/boundaries; proxy và app cùng giới hạn. |
| `max_parallel_uploads_per_principal` / `per_host` | 1 / 2 | Lease/quota server; từ chối khi hết quota. |
| Upload / scan timeout | 120 / 60 giây | Dừng tác vụ lỗi; không commit file chưa quét xong. |
| Request app / proxy response timeout | 240 / 250 giây | Proxy dài hơn app; thao tác dài chuyển durable job theo API. |
| Staging grace / quota | 3.600 giây / 100 MiB | Chỉ dọn staging hết lease, không reference committed; quota không vượt free disk gate. |
| Minimum free disk | 2 GiB | Dừng nhận trước hết đĩa; không ghi nhận false success. |

Loại tệp v0.1: UTF-8 `.txt/.log/.json/.csv`, PDF không mã hóa, PNG và JPEG. Kiểm extension, MIME/content signature, cấu trúc có giới hạn, checksum và scanner; không dựa riêng MIME client. Không nhận archive/executable hoặc nội dung không quét được; không giải nén/chạy file bằng quyền ứng dụng. External references là metadata và không tự fetch. Download luôn qua handler kiểm quyền, attachment và `Cache-Control: private, no-store`; không công bố đường dẫn file trực tiếp.

Chọn **ClamAV 1.4 LTS** chạy qua Unix socket local, một scan/lần; signature được `freshclam` cập nhật. Khóa patch, package hash, signature version và policy cập nhật trước build. Dòng 1.4 có mốc hỗ trợ patch dự kiến 15/08/2027 theo [chính sách ClamAV](https://docs.clamav.net/faq/faq-eol.html), được đối chiếu 20/10/2026; kiểm lại chính sách tại build. Không mở listener scanner ra mạng. Signature quá 86.400 giây, engine lỗi, timeout hoặc file không quét được đều fail closed. CLEAN chỉ cho qua kiểm tra kỹ thuật file, không tạo `VerificationDecision` nghiệp vụ.

Evidence root ngoài web root, staging/committed cùng filesystem, tên server sinh và không nhận path client. File và DB có lifecycle/reconciliation riêng theo [storage-transactions-v0.1.md](storage-transactions-v0.1.md). `storage_state`, trạng thái xác minh và review là các chiều độc lập; ngưỡng file không làm thay điểm RM-01.

## 5. Seed RBAC có nguồn và phạm vi cụ thể

Seed giữ nguyên fixture gốc, lấy các role/user có `application = VDT`, hợp quyền theo ID từ `permission_additions` của FLOW, sau đó thêm hai mở rộng bước 05 có lý do. Không sửa các fixture hoặc cấp quyền CRM. Các hash nguồn ghi trong JSON:

| Nguồn | SHA-256 |
| --- | --- |
| `lab-fixtures-v0.1.json` | `854b6ea530a957ca0bd2830b4ecc15ba11ab0bbe755a2b8f2bdd546dc350aef1` |
| `flow-fixtures-v0.2.json` | `820fe1a8722c07ea81a61e4865c9f89457e78f95fbc1ff845528cf6b4708497a` |

| Role | Quyền cần đồng bộ | Phạm vi |
| --- | --- | --- |
| `VDT_SECURITY` | `evidence.read_assigned`, `evidence.verify` từ FLOW; `report.read` từ RBAC-05-01 | Vận hành trên scope được cấp; không được review độc lập công việc chính mình. |
| `VDT_REVIEWER` | `evidence.read_assigned` từ fixture gốc; `evidence.verify` từ FLOW | Assessment được giao và evidence liên kết; U004 hết hạn 31/10/2026 17:00 +07:00. |
| `VDT_RISK_OWNER` | `risk.priority_approve` từ FLOW; `assessment.adjudicate` từ RBAC-05-02 | Risk sở hữu/được ủy quyền; adjudicator phải khác assessor và reviewer đang tranh chấp. |
| `VDT_ADMIN` | Giữ `organization.manage`, `users.manage`, `roles.assign` | Quản trị organization/users/roles; không suy ra quyền đọc evidence/report hoặc duyệt risk. |

`report.read` bổ sung cho Security đáp ứng TUC-08 trong self-assessment; export vẫn kiểm từng reference và đọc bytes cần `evidence.read_assigned`. `assessment.adjudicate` cho Risk Owner cho phép quyết định giải quyết tranh chấp thành snapshot mới khi bảo đảm độc lập; không cấp `assessment.run`, `evidence.verify` hoặc tự tạo SME approval. Nếu thiếu người độc lập, giữ kết quả cần review.

Seed chứa 4 roles, 19 permission codes, 4 VDT users và 4 assignment mẫu. RBAC-05-03 materialize hai chi nhánh `BR-HCM/BR-DN`, `AST-CRM`, `ASM-DEMO-01` trong scope mẫu. Mọi chiều scope đã nêu phải đồng thời khớp; không dùng home branch của user như quyền tự động. Assessment/asset/branch mới bị từ chối đến khi có grant cụ thể. Scope mẫu phải được người vận hành phê duyệt trước provisioning thật; các ID giả lập phải map sang ID cùng organization.

Trước seed: kiểm hash hai nguồn và `FLOW.base_sha256`, từ chối role/permission lạ, deduplicate `(role_id, permission_code)`, kiểm FK, giữ expiry và provenance. Role permissions chỉ là danh mục quyền; mỗi `role_assignment` còn phải thỏa active user, scope, expiry và độc lập actor. Không cho null expiry bỏ qua session expiry. Không tự seed credential, MFA enrollment, evidence, risk decision, priority approval hoặc closure. Các `acceptance_cases` trong JSON vẫn `NOT_RUN`.

Closure dùng `treatment.approve` và quyết định có lý do/tiêu chí/scope; VERIFIED, giảm R hoặc `risk.accept` không tự đóng gap/task. Các quyền bổ sung không thay trạng thái `MF-03/MF-04 = NOT_RANKED`.

## 6. Các giá trị còn phải chốt trước bước 06

| Nhóm cấu hình | Dữ liệu còn thiếu | Gate cần có trước chạy phần tương ứng |
| --- | --- | --- |
| Môi trường VDT | Origin, allowed hosts, proxy addresses, TLS/CA trust, time sync, secret refs, evidence root | HTTPS/browser trust, chỉ proxy truy app, app không là DB owner, quyền file và kết nối đúng môi trường. |
| Phiên VDT | Idle/absolute timeout, attempt window/lockout, cấp tài khoản/reset policy | Giá trị được duyệt; negative tests hết hạn/thu hồi/rate limit. |
| CRM | Năm trường bắt buộc và ngưỡng/policy phụ ở mục 3; product/build, URL, namespace cookie, login routes | Profile có version và approval; preflight CE-01/TC-01; không bắt đầu T01–T24 khi chưa đủ. |
| SC-01 | Network scope/authorization, VPN precondition evidence, dữ liệu lab | Không suy ra VPN/CRM sẵn có từ sơ đồ. |
| SC-02 | Receiver, allowed destinations, export policy, egress protocols và scope owner | T24 giữ NOT_READY nếu thiếu điều kiện; không suy giảm G vì MFA đăng nhập mới. |
| Scanner/build | Patch/hashes/signature/socket/policy cập nhật | Kiểm support/advisory, signature age, fail-closed và RAM thực tế. |
| Backup | Đích khác volume, key/operator, chu kỳ, retention, RPO/RTO | Backup DB + manifest file nhất quán, restore kiểm hash/references và session revocation. |
| Đo tài nguyên | Dự kiến VM 2 vCPU/6 GiB RAM/60 GiB disk | Đo với payload/scan/report thực ở bước 06; không coi số dự kiến là SLA. |

Số giới hạn VDT đã chọn trong JSON là điểm khởi đầu thiết kế; thay đổi phải tạo revision có lý do. Các ngưỡng CRM, môi trường lab và business impact không có giá trị mặc định được phê duyệt. `readiness.vdt_deployment` và `readiness.crm_lab` đều giữ `TO_SET_BEFORE_LAB`; parsing JSON hoặc lint tài liệu không chuyển readiness thành READY.

## 7. Truy vết và giới hạn xác nhận

| Yêu cầu | Thiết kế đáp ứng |
| --- | --- |
| Lưu ý 3.1 | Mục 4: proxy/TLS, auth/CSRF/gate, multipart limits và recheck trước commit. |
| Lưu ý 3.2; FLOW-01–04 | Mục 5: merge quyền có nguồn, scope, expiry, Risk Owner phê duyệt. |
| Lưu ý 3.3 | Trạng thái file/xác minh/assessment/review giữ độc lập trong schema/API; config không tự gán kết quả. |
| Lưu ý 3.4; SC-01 | Mục 3: trường typed CRM, ví dụ tách khỏi giá trị hiệu lực, profile version bất biến. |
| SC-02; FLOW-07 | Mục 6: receiver/egress/export policy và preflight theo scope. |
| FLOW-08–10; retest | Phiên bản config/evidence, độc lập actor, quyết định closure và kiểm quyền khi publish/download. |

Rà soát bước 05 kiểm cấu trúc JSON, phép hợp quyền và hash nguồn; chưa thực thi auth, scanner, DB constraint hoặc request. `FLOW-01…10`, `TC-01:T01…T24` và `VALID-G-01` vẫn `NOT_RUN`; A/B chưa có kết quả. Chưa có evidence CRM/SME calibration/lab, không có chứng nhận pháp lý hoặc xác nhận control hiệu lực từ mẫu cấu hình này.
