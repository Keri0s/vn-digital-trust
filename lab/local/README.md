# Môi trường phát triển local Bước 06

**Hiện có:** PostgreSQL riêng, image backend và các lệnh kiểm thử nền. **Chưa có:** CRM, VPN, receiver, Caddy/TLS, scanner daemon hoặc UI nghiệp vụ. Xem [trạng thái](../../docs/implementation/README.md) và [phương án CRM](../../docs/implementation/local-crm-lab-plan-v0.1.md).

## Dựng lại từ thư mục gốc repository

Cần Docker Desktop với Linux containers và Python trên host để sinh secrets. Mở Docker Desktop trước. Các lệnh dưới dùng file môi trường bị ignore; không hiển thị secrets. Không dùng `docker compose config` trong log chia sẻ vì nó có thể in giá trị môi trường.

```powershell
python lab/local/init_environment.py
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml up -d db
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml build app
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/database.py migrate
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py seed_rbac_catalog
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/verify_catalog.py --output /reports/rbac-catalog-checks.json
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm unit-check
```

`init_environment.py` giữ nguyên secrets nếu đã có. Trên Windows, `.runtime` dùng ACL của tài khoản/thư mục hiện tại; mode POSIX trong script không thay ACL Windows. Không chép `.runtime/local.env` vào báo cáo, Git hoặc ảnh container.

Kết quả mới ghi vào `.runtime/checks/database-checks.json`, `rbac-catalog-checks.json` và `unit-checks.json`. Chỉ chép báo cáo đã kiểm tra vào `docs/implementation/` khi ghi nhận một mốc. Bộ unit chạy không có mạng. Lệnh database check chỉ chấp nhận cấu hình local rõ ràng `VDT_LOCAL_FOUNDATION_ONLY=true` và database `vdt_step06`; script kiểm dữ liệu tổng hợp bằng transaction rollback, không reset DB. Catalog đúng seed được giữ; dữ liệu drift của bài kiểm được rollback.

## Kiểm Django và xem trạng thái

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py makemigrations --check --dry-run
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py check --deploy
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml ps
```

Lần kiểm 2026-10-23 còn W005/W021 về HSTS subdomains/preload. Không bỏ cờ secure cookie hoặc HTTPS redirect để mở UI trong lúc chờ reverse proxy. Profile `app` là khung phục vụ tích hợp về sau, không bật trong mốc này. Cổng 8000 chỉ nội bộ container; mọi API upload sau này phải đi qua reverse proxy/TLS và Policy gate.

## Dữ liệu và quyền

- Image, build cache và named volume trên máy hiện tại được lưu vật lý dưới `D:\Projects\vn-digital-trust\.runtime\docker-desktop`; đường cũ ở C dùng junction. Xem [biên bản chuyển ổ](../../docs/implementation/docker-storage-v0.1.md). Không đổi tên/xóa thư mục này khi Docker còn sử dụng. Trên máy mới, xác nhận Disk image location trước khi pull/build để không tăng dữ liệu ở ổ hệ thống.
- PostgreSQL bind `127.0.0.1:55432`, volume `vdt-step06_vdt_pgdata`, không dùng database sẵn có.
- `vdt_owner` là superuser phục vụ bootstrap/migration local. Chỉ service `admin` nhận credential này. App dùng `vdt_app` với quyền runtime hạn chế; schema migration không chạy bằng tài khoản app.
- DB cap 1536 MiB; app/admin/unit cap 1024 MiB mỗi container. Đây là giới hạn cấu hình, chưa là số đo tài nguyên hay bảo đảm chạy toàn bộ CRM trên máy 16 GB.
- Đã nạp danh mục 4 role/19 permission/22 liên kết; chưa có business account, role assignment, mật khẩu chung, CRM evidence hoặc SME approval được tạo. Tài khoản/quyền theo scope/phiên là mốc tiếp theo.
- Chưa có backup/restore. Dừng môi trường bằng lệnh dưới giữ volume; không dùng tùy chọn xóa volume nếu cần giữ dữ liệu.

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml stop
```
