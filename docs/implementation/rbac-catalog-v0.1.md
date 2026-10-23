# Khởi tạo danh mục quyền RBAC — 2026-10-23

**Đã áp dụng vào database local:** 19 permission, 4 role, 22 role_permission. Không tạo tổ chức, người dùng, scope, role assignment, credentials hoặc approval. Danh mục không tự cấp quyền truy cập.

## Nguồn và quy tắc

Lệnh `seed_rbac_catalog` kiểm canonical JSON hash của [RBAC-05](../design/rbac-seed-v0.1.json), raw SHA-256 của fixture LAB/FLOW và `FLOW.base_sha256`. Lệnh dựng lại phép hợp baseline → FLOW additions → Step 05 extensions. Hash nguồn và số bản ghi nằm trong [báo cáo thực thi](rbac-catalog-checks-v0.1.json). 29 file thiết kế Bước 05 đã được đối chiếu với gói bàn giao; bytes không đổi.

UUIDv5 được sinh từ namespace có version và mã quyền/vai trò/liên kết; chạy lại giữ nguyên UUID. Cột description của role lưu application/scope/scope_constraint dưới dạng mô tả; object scope chỉ có hiệu lực khi service tạo role assignment hợp lệ.

| Vai trò | Tổng quyền | Các quyền người dùng yêu cầu |
| --- | ---: | --- |
| VDT_ADMIN | 3 | Không được suy ra quyền đọc evidence hoặc risk priority |
| VDT_SECURITY | 9 | evidence.verify, evidence.read_assigned |
| VDT_REVIEWER | 4 | evidence.verify, evidence.read_assigned; assignment còn hạn vẫn bắt buộc |
| VDT_RISK_OWNER | 6 | risk.priority_approve |

Thực thi dùng transaction, advisory lock và table locks; chỉ thêm các dòng còn thiếu khi dữ liệu đang có là tập con đúng của catalog. Sai UUID, description, mapping hoặc có dòng ngoài catalog làm lệnh từ chối, không tự sửa/xóa. Nếu đã có role assignment thì việc thêm catalog bị chặn để tránh mở rộng quyền ngầm; thay đổi quyền lúc vận hành cần workflow riêng.

## Kiểm tra đã thực hiện

- 12 unit tests về provenance, ba quyền yêu cầu, JSON/hash, projection, chạy lặp và drift; nằm trong tổng 121 tests.
- 10 kiểm tra PostgreSQL thực tế: nạp từ 0 lên 19/4/22; đủ năm cặp role/quyền yêu cầu; chạy lại không đổi row/UUID; không tạo tổ chức/user/scope/assignment; drift description bị từ chối và rollback; runtime đọc được nhưng UPDATE từng bảng catalog bị từ chối với SQLSTATE 42501.
- Tài khoản runtime `vdt_app` đã bị thu hồi INSERT/UPDATE trên permission/role/role_permission; bootstrap chạy bằng `vdt_owner`. Chưa kiểm cạnh tranh nhiều kết nối hoặc thay đổi catalog khi có assignment thật.

## Lệnh vận hành local

Từ thư mục gốc dự án sau migration:

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py seed_rbac_catalog
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py seed_rbac_catalog --check
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/verify_catalog.py --output /reports/rbac-catalog-checks.json
```

`--validate-only` chỉ kiểm file nguồn, không kết nối DB. `--check` yêu cầu catalog trong DB đã đủ và đúng, không ghi dữ liệu. `verify_catalog.py` chỉ cho database local `vdt_step06` với opt-in của runbook; nó nạp catalog rồi thử drift trong transaction rollback. Không dùng runner này như lệnh kiểm production.

Các account/expiry trong fixture là thiết kế lịch sử, chưa được materialize thành phiên/quyền vận hành. FLOW/TC/VALID-G giữ NOT_RUN; seed catalog không là kết quả kiểm thử CRM hay phê duyệt SME.
