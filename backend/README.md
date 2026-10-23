# VN Digital Trust backend — Step 06 foundation

Trạng thái và giới hạn: [hồ sơ Bước 06](../docs/implementation/README.md). Dựng/chạy kiểm thử: [local runbook](../lab/local/README.md).

Các module hiện có: `vdt.configuration`, `vdt.policy`, `vdt.risk`, `vdt.evidence`; migration PostgreSQL, AppUser mapping và lệnh `seed_rbac_catalog` trong `vdt.core`. Danh mục role/permission đã nạp; chưa có role assignment. Chúng chưa được nối thành API nghiệp vụ. `vdt.urls` chỉ mở trang thông báo, liveness và CSRF; API khác trả 503. Chưa có dịch vụ đăng nhập hoặc tài khoản đăng nhập.

Không dùng các cờ confirmation, principal, scope, grant hoặc ScanResult do client cung cấp như dữ liệu đã xác minh. Tầng dịch vụ sắp triển khai phải lấy chúng từ DB/phiên/adapter tin cậy, giữ authorization guard và kiểm lại trước commit, stream, export. `promote()` của file store chỉ chuyển tệp vật lý; không tự ghi `COMMITTED`, quyết định verification hoặc closure.
