# Môi trường phát triển local Bước 06

**Cập nhật 2026-10-26 · IN_PROGRESS.** Đã bổ sung quản lý người dùng và phân quyền tại **https://localhost:8443/admin/users**, bên cạnh đăng nhập, phiên, đổi mật khẩu và đăng xuất. Trạng thái triển khai mốc quản trị: **DEPLOYED_LOCAL — https://localhost:8443/admin/users**. Chưa có CRM, VPN, receiver, scanner daemon hoặc luồng UI nghiệp vụ hoàn chỉnh. Xem [trạng thái triển khai](../../docs/implementation/README.md) và [phương án CRM](../../docs/implementation/local-crm-lab-plan-v0.1.md).

## Việc cần làm trên máy hiện tại

CA local đã được xác minh và cài vào `CurrentUser\Root`; không cần nhập lại. Người dùng đã tạo tài khoản quản trị, báo cáo đăng nhập, đổi mật khẩu và thử sai năm lần dẫn đến thông báo tạm khóa 15 phút đều hoạt động. Tiếp tục dùng tài khoản hiện có; không chạy lại bootstrap. Chưa ghi nhận kiểm tra thủ công đăng xuất hoặc tự mở khóa sau khi chờ đủ 15 phút.

Mở **https://localhost:8443/admin/users** sau khi đăng nhập. Xem [hướng dẫn tạo người dùng, mật khẩu tạm và cấp quyền](../../docs/implementation/access-management-v0.1.md). Nếu cần khởi động lab, mở PowerShell:

```powershell
Set-Location "D:\Projects\vn-digital-trust"
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile app up -d db app proxy
```

Chỉ dùng lệnh `bootstrap_local_admin` theo [hướng dẫn đăng nhập](../../docs/implementation/login-v0.1.md) khi dựng môi trường mới chưa có admin. Không có mật khẩu chung hoặc mật khẩu mặc định.

## Dựng lại hoặc cập nhật phiên bản

Cần Docker Desktop với Linux containers và Python trên host để sinh secrets. Mở Docker Desktop trước. Chạy các lệnh từ thư mục gốc repository. Không dùng `docker compose config` trong log chia sẻ vì nó có thể in giá trị môi trường.

```powershell
python lab/local/init_environment.py
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml up -d db
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml build app
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/database.py migrate
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py seed_rbac_catalog
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile app up -d app proxy
```

`init_environment.py` giữ nguyên secrets nếu đã có. Trên Windows, `.runtime` dùng ACL của tài khoản/thư mục hiện tại; mode POSIX trong script không thay ACL Windows. Không chép `.runtime/local.env` vào báo cáo, Git hoặc ảnh container.

Trên máy mới, xuất CA công khai từ proxy và xác minh trước khi tin cậy theo [hướng dẫn đăng nhập](../../docs/implementation/login-v0.1.md). Chỉ nhập vào `CurrentUser\Root`; không sao chép khóa riêng của CA. Thumbprint đã xác minh trên máy hiện tại: `75F583CD759A86D3DEF7C0B16B8F78CD7222AB2F`. Máy dựng mới có CA riêng nên phải xác minh bản của máy đó.

## Kiểm thử

### Unit, database nền và danh mục quyền

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm unit-check
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/verify_catalog.py --output /reports/rbac-catalog-checks.json
```

Kết quả ghi vào `.runtime/checks/unit-checks.json`, `database-checks.json` và `rbac-catalog-checks.json`. Bộ unit chạy không có mạng. Database foundation check chỉ chấp nhận local được khai báo rõ `VDT_LOCAL_FOUNDATION_ONLY=true` và database `vdt_step06`; dữ liệu tổng hợp được rollback, không reset DB. Catalog đúng seed được giữ; dữ liệu drift của bài kiểm được rollback. Nếu kiểm tra yêu cầu database chưa có dữ liệu, không xóa tài khoản đã tạo để chạy lại; dùng môi trường test riêng.

### Đăng nhập trên PostgreSQL tạm riêng

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml up --abort-on-container-exit --exit-code-from check
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml down
```

Compose test dùng project `vdt-auth-test`, PostgreSQL trong `tmpfs` và mạng nội bộ riêng. Request kiểm thử dùng role `vdt_app`; quyền owner chỉ phục vụ setup và tạo tình huống hết hạn/thu hồi trong DB tạm. Tài khoản tổng hợp nằm trong DB test; `down` trên đúng file test kết thúc môi trường tạm. Báo cáo giữ ở `.runtime/checks/auth-checks.json`.

### Quản lý tài khoản và quyền trên PostgreSQL tạm riêng

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.access-test.yaml down
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.access-test.yaml run --rm check
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.access-test.yaml down
```

Hai file test tạo project **`vdt-access-test`**, tách khỏi project vận hành `vdt-step06`. Database test nằm trên tmpfs; runner từ chối môi trường khác `PGHOST=testdb`, các cờ test/local không đúng hoặc testdb đã có tài khoản. `down` trong các lệnh trên chỉ dọn project test, không reset database lab thật. Báo cáo ở `.runtime/checks/access-checks.json`; chỉ đưa bản đã kiểm tra không chứa bí mật vào hồ sơ triển khai.

Bộ kiểm tra dùng HTTP Django có CSRF và đường proxy giả lập, với kết nối database `vdt_app`; kiểm phiên bản/dependencies, gửi trùng và cạnh tranh, scope/thời hạn, thu hồi, mật khẩu tạm, lịch sử và nhật ký. Đây không phải bằng chứng browser/TLS thực; hai nhóm đó được ghi riêng.

Khi QA giao diện cần tài khoản tổng hợp, runner hỗ trợ `--browser-fixture-output /reports/access-browser-fixture.json`. Chỉ sinh file sau khi toàn bộ kiểm tra đạt. Tệp này nằm riêng trong `.runtime/checks`, chứa credential tổng hợp và không được chép vào báo cáo/Git. Profile `browser-qa` của overlay dùng testdb ở trên, cổng **8444** và tên cookie riêng, đọc chứng chỉ local từ volume Caddy hiện có. Sau QA phải dừng project test và dọn đúng tệp credential. Không dùng mật khẩu admin thật để thay thế fixture.

**Mốc quản trị 2026-10-26:** unit **143/143 đạt**; access integration **27/27 đạt**; auth regression **22/22 đạt**; browser **12/12 kiểm tra thủ công bằng tài khoản tổng hợp đạt**; kiểm cập nhật lab thật **Đạt: giữ nguyên 1 tài khoản/1 lượt cấp quyền và thông tin xác thực; 16/16 database, 12/12 HTTPS auth, 11/11 HTTPS quản trị**.

### HTTPS thật trên Windows

Khi proxy đang chạy và Windows đã tin cậy CA local:

```powershell
& .\lab\local\verify_https.ps1
& .\lab\local\verify_access_https.ps1
```

Script dùng kho tin cậy Windows, không bỏ qua xác minh TLS. Báo cáo `.runtime/checks/https-checks.json` kiểm trang đăng nhập, tài nguyên, CSRF, nguồn yêu cầu và ranh giới chưa đăng nhập; không sử dụng mật khẩu thật của operator.

**Mốc 2026-10-24:** 143/143 unit, 22/22 auth integration, 16/16 database foundation và 12/12 HTTPS checks đạt. Tám yêu cầu sai đồng thời cho đúng 5×401 + 3×429. Trình duyệt ở mốc đó đã kiểm trang đăng nhập, thông báo sai và xóa mật khẩu. Sau mốc này, người dùng đã báo cáo các thao tác thành công nêu ở đầu trang. Chỉ chép báo cáo đã kiểm tra vào `docs/implementation/` khi ghi nhận một mốc.

## Kiểm Django và trạng thái service

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py makemigrations --check --dry-run
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py check --deploy
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml ps
```

Deployment check còn W005/W021 về HSTS subdomains/preload, được giữ có chủ đích cho localhost. Cookie vẫn bắt buộc HTTPS. Cổng 8000 chỉ nội bộ container; API xác thực nhận yêu cầu qua proxy tin cậy. API quản trị kiểm quyền hiện hành trong authorization guard và kiểm lại trước khi hoàn tất. Endpoint nghiệp vụ chưa mở trả 401 khi chưa đăng nhập, 403 khi còn phải đổi mật khẩu tạm và 503 cho phiên đủ điều kiện. Policy gate theo đối tượng/phạm vi và recheck khi stream bằng chứng còn cần tích hợp.

## Dữ liệu, phiên và quyền

- Image, build cache và named volume trên máy hiện tại nằm dưới `D:\Projects\vn-digital-trust\.runtime\docker-desktop`; đường cũ ở C dùng junction. Xem [biên bản chuyển ổ](../../docs/implementation/docker-storage-v0.1.md). Không đổi tên/xóa thư mục này khi Docker còn sử dụng. Trên máy mới, xác nhận vị trí dữ liệu Docker trước khi pull/build.
- Proxy bind `127.0.0.1:8443`; PostgreSQL bind `127.0.0.1:55432`, volume `vdt-step06_vdt_pgdata`. App không xuất cổng trực tiếp ra host.
- `vdt_owner` là superuser phục vụ bootstrap/migration local. Chỉ service `admin` nhận credential này trong môi trường vận hành local. App dùng `vdt_app` với quyền runtime hạn chế; schema migration không chạy bằng tài khoản app.
- DB cap 1536 MiB; app/admin/unit cap 1024 MiB mỗi container; proxy cap 256 MiB. Đây là giới hạn cấu hình, chưa là số đo tài nguyên hay bảo đảm chạy toàn bộ CRM trên máy 16 GB.
- Đã nạp 4 role/19 permission/22 liên kết; người dùng đã tạo admin riêng. Không có mật khẩu chung được tạo sẵn. Danh mục quyền tự nó không cấp quyền; lượt cấp cần scope và thời hạn phù hợp. ADMIN hiện chỉ hỗ trợ toàn tổ chức; UI Security/Risk Owner theo chi nhánh; Reviewer UI chọn đợt đánh giá thật đang mở và bắt buộc có hạn.
- Profile `DEVELOPMENT_LOCAL`: idle 30 phút, absolute 8 giờ, 5 lần sai trong cửa sổ 15 phút thì tạm khóa 15 phút. GET phiên không gia hạn idle. Chính sách VDT local không đặt giá trị thay cho AUTH-CRM-01.
- Chưa có CRM evidence, SME approval hoặc nghiệm thu Bước 06; chưa kiểm chứng phục hồi từ bản sao lưu. FLOW/TC/VALID-G vẫn NOT_RUN.

Dừng môi trường và giữ dữ liệu:

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml stop
```

Không dùng tùy chọn xóa volume khi cần giữ dữ liệu và CA local.
