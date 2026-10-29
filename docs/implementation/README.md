# Bước 06 — triển khai prototype và lab local

**Cập nhật 2026-10-27 · IN_PROGRESS · Mốc hiện tại: hệ thống/tài sản → bối cảnh → kịch bản → hồ sơ consultant.**

**DEPLOYED_LOCAL:** phần [chuẩn bị hồ sơ](workspace-v0.1.md) đã chạy tại **https://localhost:8443/workspace**. Security khai báo hệ thống, tài sản, dữ liệu, lưu bối cảnh, tạo kịch bản và thêm phiên bản đang sử dụng vào đợt. Consultant đọc nội dung được giao, gồm nguồn và inventory tại thời điểm lưu. Bản cập nhật giữ nguyên **4 tài khoản, 4 lượt cấp quyền và 1 đợt đánh giá**; chưa tự thêm dữ liệu mẫu vào lab thật.

Kiểm chứng mốc 2026-10-27: **60/60 workspace, 143/143 unit, 39/39 assessment, 22/22 auth, 16/16 database, 12/12 HTTPS nền và 11/11 HTTPS workspace**. Browser đã đi hết luồng tạo hệ thống → bối cảnh → nháp → sử dụng → gắn vào đợt → consultant đọc bằng hai tài khoản tổng hợp ở database riêng. Xem [báo cáo browser](workspace-browser-checks-v0.1.json), [ảnh hồ sơ](workspace-consultant-v0.1.png), [ảnh kịch bản](workspace-scenario-v0.1.png) và [biên bản triển khai](workspace-deployment-v0.1.json). Upload/xác minh bằng chứng và gửi kết luận thẩm định chưa được mở.

Ứng dụng local tại **https://localhost:8443**; trang quản trị tại **https://localhost:8443/admin/users**. Người dùng đã tạo tài khoản quản trị và báo cáo đăng nhập, đổi mật khẩu, thử sai năm lần dẫn đến thông báo khóa 15 phút đều hoạt động. Tiếp tục dùng tài khoản đó; không chạy lại bootstrap. Chưa ghi nhận người dùng kiểm tra đăng xuất hoặc tự mở khóa sau 15 phút.

Mốc quản trị trước đó đã triển khai tại https://localhost:8443/admin/users. Xem [hướng dẫn quản lý người dùng và phân quyền](access-management-v0.1.md). Bước 06 chưa hoàn thành; CRM và các luồng nghiệp vụ còn đang triển khai.

Đã thêm [đợt đánh giá và giao Reviewer](assessment-worklist-v0.1.md) tại **https://localhost:8443/assessments**. Tài khoản Security có thể tạo đợt theo chi nhánh đã cấp; Admin giao một đợt đang mở cho Reviewer có thời hạn. 11/11 kiểm tra tích hợp trên database tạm đạt. Người dùng đã xác nhận hoàn thành một vòng quản lý tài khoản; database lab vẫn giữ 2 tài khoản và 2 lượt cấp quyền sau cập nhật.

Đã sửa lỗi ẩn nút **Đợt đánh giá** do phiên đăng nhập chưa trả quyền điều hướng nghiệp vụ. Bản sửa đạt 26/26 kiểm tra assessment/navigation, 22/22 auth và 143/143 unit; đã kiểm tra trên trình duyệt bằng phiên đang mở và thấy form tạo đợt tải được. Xem [biên bản và ảnh kiểm chứng](assessment-worklist-v0.1.md).

Đã sửa tên chi nhánh cho các vai trò chỉ đọc và thêm **Mở hồ sơ** với quyền, phạm vi và thời hạn thật. Bản sửa đạt 39/39 kiểm tra assessment và 143/143 unit, đã mở thử hồ sơ bằng phiên consultant hiện có. Các thao tác mở bằng chứng, yêu cầu bổ sung và gửi kết luận thẩm định **chưa được triển khai**; giao diện ghi rõ giới hạn này. Xem [chi tiết và ảnh](assessment-worklist-v0.1.md#tên-chi-nhánh-và-hồ-sơ-consultant--2026-10-26).

## Đã có

| Hạng mục | Kết quả/phạm vi | Giới hạn |
| --- | --- | --- |
| Môi trường | Python 3.13.17, Django 5.2.18, DRF 3.16.1, PostgreSQL 17.11; dependency hash lock | Môi trường phát triển local |
| Database | 106 bảng domain và 1 bảng vận hành xác thực; migration 0004 lưu liên kết phiên bản kịch bản | Đã sao lưu trước cập nhật; kiểm cạnh tranh workspace đạt; chưa kiểm phục hồi backup |
| Danh mục RBAC | 4 role, 19 permission, 22 liên kết; danh mục chỉ đọc bằng tài khoản runtime | Giữ hồ sơ lịch sử của [mốc RBAC](rbac-catalog-v0.1.md) |
| Đăng nhập và phiên | Login/logout, idle/absolute expiry, khóa thử sai, đổi mật khẩu, thu hồi phiên; mốc đăng nhập có 22/22 kiểm tra tích hợp đạt | Kết quả mốc 2026-10-24 được giữ riêng; hồi quy mới xem dưới |
| Quản trị tài khoản | Tạo/sửa/khóa hồ sơ, mật khẩu tạm bắt buộc đổi, cấp/thu hồi role, phạm vi chi nhánh, thời hạn, nhật ký | ADMIN toàn tổ chức; Reviewer cần đợt đánh giá thật và thời hạn; không tự có quyền nghiệp vụ |
| Chuẩn bị hồ sơ | Inventory, context snapshot, scenario DRAFT/ACTIVE/RETIRED, gắn phiên bản vào đợt và dossier consultant | Một chi nhánh/hồ sơ; liên kết inventory chỉ bổ sung; chưa có vendor/data-flow hoặc evidence source |
| Kiểm quyền khi ghi | Kiểm phiên/quyền hiện hành trong authorization guard, CSRF, idempotency, phiên bản, phụ thuộc, history/audit | Policy gate đầy đủ theo đối tượng và kiểm lúc stream bằng chứng còn cần tích hợp |
| HTTPS và UI | Caddy trên loopback; mốc đăng nhập có 12/12 kiểm tra HTTPS thật đạt | Kết quả browser và lab của mốc quản trị ghi ở bảng kiểm chứng |
| Risk | RM-01, UNKNOWN/ranges, max G theo đường và impact comparison; 48 kiểm thử của mốc nền | Chưa có API hoặc persistence nghiệp vụ |
| Evidence | Stage/hash/format/scan protocol/promote/read/cleanup; 25 kiểm thử của mốc nền | Chưa chạy scanner daemon hoặc tích hợp DB/job/upload |
| Cấu hình CRM | Template bị chặn khi thiếu cấu hình và phê duyệt | Năm trường AUTH-CRM-01 chưa chốt; không tự dùng ví dụ 120/5/900 |

## Kiểm chứng mốc quản trị — 2026-10-26

| Nhóm kiểm tra | Kết quả thực tế |
| --- | --- |
| Unit/contract và hash nguồn | **143/143 đạt** |
| API quản trị trên PostgreSQL tạm | **27/27 đạt** |
| Hồi quy đăng nhập | **22/22 đạt** |
| Trình duyệt với dữ liệu tổng hợp riêng | **12/12 kiểm tra thủ công bằng tài khoản tổng hợp đạt** |
| Cập nhật lab thật, giữ tài khoản hiện có | **Đạt: giữ nguyên 1 tài khoản/1 lượt cấp quyền và thông tin xác thực; 16/16 database, 12/12 HTTPS auth, 11/11 HTTPS quản trị** |

Tài khoản kiểm thử nằm trong `testdb` riêng; request dùng role database runtime `vdt_app`. Kết quả thử nghiệm không phải nghiệm thu CRM hoặc nghiệm thu toàn bộ Bước 06. Xem [hướng dẫn quản trị](access-management-v0.1.md) và [cách tái lập](../../lab/local/README.md).

CA local đã được xác minh và cài vào `CurrentUser\Root` sau khi người dùng đồng ý; thumbprint `75F583CD759A86D3DEF7C0B16B8F78CD7222AB2F`. Cổng 8443 chỉ mở trên loopback, ứng dụng 8000 chỉ nội bộ container, PostgreSQL tại `127.0.0.1:55432`. Image/build cache/volume tiếp tục lưu vật lý trong dự án ở D theo [biên bản chuyển ổ](docker-storage-v0.1.md).

Các API nghiệp vụ chưa mở trả 401 khi chưa đăng nhập, 403 khi còn yêu cầu đổi mật khẩu tạm và 503 `PROTOTYPE_NOT_READY` với phiên đủ điều kiện. API assessment và [API workspace](workspace-api-addendum-v0.1.md) đã mở theo quyền và scope. Kiểm tra Django deployment hiện tại còn W005/W021 về HSTS subdomains/preload, giữ có chủ đích cho localhost; chưa nghiệm thu production.

Hồ sơ của mốc quản trị: [143 unit checks](unit-checks-access-v0.1.json), [27 access checks](access-checks-v0.1.json), [22 auth checks](auth-checks-access-v0.1.json), [16 database checks](database-checks-access-v0.1.json), [12 HTTPS auth checks](https-checks-access-v0.1.json), [11 HTTPS quản trị checks](access-https-checks-v0.1.json), [12 kiểm tra trình duyệt](access-browser-checks-v0.1.json), [biên bản cập nhật lab](access-deployment-v0.1.json).

Ảnh kiểm chứng trên dữ liệu tổng hợp: [máy tính](access-preview-desktop-v0.1.png), [màn hình nhỏ](access-preview-mobile-v0.1.png). Đã sao lưu trước cập nhật; chưa kiểm thử phục hồi từ backup. Database tạm và tệp mật khẩu thử đã được dọn.

## Hồ sơ lịch sử được giữ lại

### Đăng nhập — 2026-10-24

- [Hướng dẫn tạo tài khoản và đăng nhập](login-v0.1.md). Hướng dẫn bootstrap dành cho môi trường chưa có admin; máy hiện tại đã có tài khoản do người dùng tạo.
- [143 unit checks và hash mã nguồn](unit-checks-login-v0.1.json), [22 kiểm tra auth PostgreSQL](auth-checks-v0.1.json), [16 kiểm tra database nền](database-checks-login-v0.1.json), [12 kiểm tra HTTPS](https-checks-v0.1.json).
- [Ảnh trang đăng nhập](login-preview-v0.1.jpg).

Tám yêu cầu đăng nhập sai đồng thời ở mốc này cho đúng 5 phản hồi 401 và 3 phản hồi 429. Browser đã kiểm trang đăng nhập, thông báo sai và xóa mật khẩu sau khi gửi. Mô tả “chờ operator tạo admin” trong hồ sơ ngày 2026-10-24 phản ánh thời điểm đó; người dùng đã báo cáo hoàn thành các thao tác nêu ở đầu trang.

### Nền tảng và kế hoạch

- [Biên bản mốc nền](validation-v0.1.md), [121 unit checks](unit-checks-v0.1.json), [15 kiểm tra PostgreSQL nền](database-checks-v0.1.json), [10 kiểm tra RBAC](rbac-catalog-checks-v0.1.json).
- [Nguồn migration](schema-provenance-v0.1.json), [dependency lock provenance](dependency-lock-v0.1.json).
- [Phương án CRM/lab local](local-crm-lab-plan-v0.1.md), [kế hoạch chung, mục 29](../planning/execution-plan-v0.1.md).

Các báo cáo cũ là hồ sơ lịch sử và không bị ghi đè bởi lần chạy mới.

## Công việc tiếp theo

1. Nối Policy gate theo đối tượng, scanner/job, giới hạn stream và lifecycle transaction để mở upload qua Browser → Reverse proxy/TLS → Policy gate → kho bằng chứng.
2. Nối evidence/control/risk → review/treatment/retest/report; kiểm idempotency, OCC, audit, snapshot/as_of và closure xuyên suốt.
3. Dựng CRM local riêng, chốt cấu hình có provenance, chạy FLOW-01…10, T01–T24, VALID-G-01 và các kiểm tra lỗi/restore/tài nguyên.

FLOW-01…10, T01–T24, VALID-G-01: **NOT_RUN**. Phiếu G A/B trống; chưa có evidence CRM hoặc hiệu chuẩn SME. MF-03/MF-04 vẫn **NOT_RANKED**, chưa có phê duyệt ưu tiên SME.
