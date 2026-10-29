# Đăng nhập VDT local — v0.1

Ngày cập nhật: **2026-10-24**. Phạm vi: prototype Bước 06 trên máy local.

Giao diện hỗ trợ đăng nhập, xem phiên và các quyền quản trị hiện có, đổi mật khẩu, đăng xuất. Chức năng nhập bằng chứng, đánh giá, báo cáo và môi trường CRM vẫn đang được phát triển. Tài khoản VDT độc lập với tài khoản CRM; cấu hình dưới đây không thay thế `AUTH-CRM-01` và không ghi nhận phê duyệt nghiệp vụ.

## 1. Mở PowerShell đúng thư mục

Mở Docker Desktop, đợi Linux containers sẵn sàng rồi mở PowerShell:

```powershell
Set-Location "D:\Projects\vn-digital-trust"
```

Trên máy hiện tại, image, build cache và named volume của Docker được lưu vật lý tại `D:\Projects\vn-digital-trust\.runtime\docker-desktop`. Không di chuyển hoặc xóa thư mục này khi Docker còn sử dụng. Chứng chỉ local được lưu trong volume của Caddy và bản sao chứng chỉ công khai ở `.runtime/tls/`.

## 2. Chuẩn bị phiên bản đăng nhập

Các lệnh sau dành cho việc dựng lần đầu hoặc cập nhật mã đăng nhập. Nếu người triển khai đã hoàn tất chúng, tiếp tục bước 3.

```powershell
python lab/local/init_environment.py
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml up -d db
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml build app
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python /app/lab/local/database.py migrate
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py seed_rbac_catalog
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile app up -d app proxy
```

`init_environment.py` giữ nguyên secrets đã có. `.runtime/local.env` là file riêng của máy, không đưa vào Git, báo cáo hoặc cuộc trò chuyện. Service `admin` dùng tài khoản database phục vụ khởi tạo; ứng dụng dùng tài khoản runtime hạn chế quyền.

Ứng dụng truy cập qua **https://localhost:8443**. Cổng ứng dụng 8000 chỉ nằm trong mạng container. API xác nhận cổng HTTPS tin cậy, nguồn yêu cầu, CSRF và phiên hiện hành; không mở đường truy cập thẳng vào ứng dụng.

## 3. Tin cậy chứng chỉ HTTPS local

Caddy tạo CA riêng cho lab. Chứng chỉ CA công khai được xuất tới `.runtime/tls/vdt-local-root.crt`; không sao chép khóa riêng của CA.

**Máy hiện tại đã hoàn tất ngày 2026-10-24:** người dùng đã đồng ý, CA được nhập vào `CurrentUser\Root` và HTTPS đã được kiểm tra bằng kho tin cậy Windows, không tắt xác minh TLS. Dấu vân tay chứng chỉ: `75F583CD759A86D3DEF7C0B16B8F78CD7222AB2F`. Chứng chỉ tự tạo này không có phí. Không cần nhập lại trên tài khoản Windows hiện tại; các lệnh dưới phục vụ dựng lại trên máy khác hoặc khi CA thay đổi.

Nếu file chưa được xuất, chạy khi service `proxy` đang hoạt động:

```powershell
New-Item -ItemType Directory -Force -Path ".runtime\tls" | Out-Null
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml cp proxy:/data/caddy/pki/authorities/local/root.crt .runtime/tls/vdt-local-root.crt
certutil -dump ".runtime\tls\vdt-local-root.crt"
```

Trước khi nhập, kiểm tra đây đúng là CA vừa xuất từ proxy của dự án, thời hạn hợp lệ và đối chiếu dấu vân tay chứng chỉ với bản mà người triển khai đã xác minh. Việc nhập chứng chỉ thay đổi danh sách CA tin cậy của tài khoản Windows hiện tại. Chỉ thực hiện sau khi đã kiểm tra nguồn chứng chỉ.

```powershell
Import-Certificate -FilePath ".runtime\tls\vdt-local-root.crt" -CertStoreLocation "Cert:\CurrentUser\Root"
```

Lệnh dùng kho **CurrentUser**, không dùng `LocalMachine` và không cần mở PowerShell bằng quyền quản trị. Mở lại trình duyệt nếu cần. Nếu vẫn có cảnh báo, kiểm tra URL, nguồn CA và cấu hình tin cậy của trình duyệt trước khi nhập mật khẩu.

## 4. Tạo tài khoản quản trị đầu tiên

Không có mật khẩu hoặc tài khoản đăng nhập mặc định. Chạy lệnh tương tác trong PowerShell:

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile tools run --rm admin python manage.py bootstrap_local_admin
```

Nhập tên đăng nhập, tên hiển thị, mật khẩu và nhập lại mật khẩu theo lời nhắc. Khi nhập mật khẩu, màn hình không hiển thị ký tự. Mật khẩu cần **ít nhất 12 ký tự**, không phổ biến, không chỉ gồm số. Lệnh tạo dữ liệu doanh nghiệp giả lập và tài khoản quản trị đầu tiên; không tự tạo tài khoản CRM.

Không truyền mật khẩu bằng tham số, biến môi trường hoặc chuyển hướng đầu vào. Không gửi mật khẩu vào cuộc trò chuyện. Lệnh từ chối tạo đè khi tài khoản đã tồn tại; khi đó dùng tài khoản đã tạo để đăng nhập.

## 5. Đăng nhập và kiểm tra

1. Mở **https://localhost:8443** bằng trình duyệt trên máy này.
2. Nhập tài khoản vừa tạo và chọn **Đăng nhập**.
3. Kiểm tra tên hiển thị, hai mốc hết hạn phiên và danh sách quyền quản trị.
4. Thử đổi mật khẩu bằng mật khẩu hiện tại và hai lần nhập mật khẩu mới.
5. Chọn **Đăng xuất**, rồi đăng nhập lại bằng mật khẩu mới.

Quyền hiển thị trong phiên hiện chỉ gồm các quyền quản trị tổ chức áp dụng được (`organization.manage`, `roles.assign`, `users.manage`). Danh sách này không phải bằng chứng được phép truy cập một đối tượng nghiệp vụ; API nghiệp vụ về sau vẫn cần kiểm tra phạm vi riêng.

## 6. Chính sách phiên local

Các giá trị được khai báo rõ trong `lab/local/vdt-auth-policy.json`, profile `DEVELOPMENT_LOCAL`:

| Tham số | Giá trị local |
|---|---:|
| Hết hạn khi không hoạt động | 30 phút |
| Hạn tuyệt đối của phiên | 8 giờ |
| Ngưỡng thử sai | 5 lần trong cửa sổ 15 phút |
| Thời gian tạm khóa thử lại | 15 phút |

Giới hạn thử sai áp dụng theo định danh tài khoản và nguồn truy cập. GET thông tin phiên không gia hạn thời gian hoạt động; giao diện không tự gửi yêu cầu giữ phiên. Trong phạm vi chức năng hiện tại, người dùng cần đăng nhập lại khi phiên hết hạn. Đổi mật khẩu tạo phiên mới cho trình duyệt hiện tại, giữ nguyên hạn tuyệt đối ban đầu và thu hồi các phiên còn lại của tài khoản.

Cookie phiên có `Secure`, `HttpOnly`, `SameSite=Lax`; mật khẩu và token không được ghi vào `localStorage`. Thông báo đăng nhập sai không xác nhận tên tài khoản có tồn tại hay không. Mật khẩu được xóa khỏi các ô nhập sau khi gửi thao tác.

## 7. Khi gặp thông báo lỗi

| Thông báo | Cách xử lý |
|---|---|
| Không thể đăng nhập | Kiểm tra tên đăng nhập và mật khẩu; chưa có tài khoản thì làm bước 4. |
| Thử quá nhiều lần | Đợi hết thời gian tạm khóa rồi thử lại; không thử liên tục. |
| Phiên hết hạn hoặc bị thu hồi | Đăng nhập lại. |
| Mật khẩu hiện tại chưa đúng | Nhập lại trong phần đổi mật khẩu; phiên hợp lệ vẫn được giữ. |
| Mật khẩu mới không đạt yêu cầu | Chọn mật khẩu khác đáp ứng hướng dẫn trên biểu mẫu. |
| Yêu cầu chưa được xác nhận | Tải lại trang, xác nhận URL `https://localhost:8443` rồi thực hiện lại. |
| Dịch vụ chưa sẵn sàng hoặc không kết nối được | Kiểm tra Docker Desktop và trạng thái các service bên dưới. |

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml ps
```

Xem kết quả kiểm thử thực tế và phần còn dang dở tại [hồ sơ triển khai](README.md). Các kiểm thử đăng nhập không thay thế kiểm thử CRM, luồng nghiệp vụ, phục hồi dữ liệu hoặc nghiệm thu Bước 06.

## 8. Tái lập kiểm thử đăng nhập

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml run --rm check
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml down
powershell -NoProfile -File lab/local/verify_https.ps1
```

Bộ tích hợp chỉ chấp nhận `PGHOST=testdb` và các cờ local/test rõ ràng; dữ liệu tài khoản thử nằm trên tmpfs của service riêng. Lệnh `down` ở trên chỉ dọn môi trường `vdt-auth-test`, không tác động database lab thật. Không chạy lại bộ tích hợp khi testdb còn chứa tài khoản của lần trước; dọn đúng môi trường thử trước khi chạy lại. Bộ HTTPS không tạo tài khoản và cần CA đã được tin cậy.

Kết quả ngày 2026-10-24: [22/22 tích hợp PostgreSQL](auth-checks-v0.1.json), [12/12 HTTPS](https-checks-v0.1.json); trình duyệt tải đúng UI, thông báo sai tài khoản và xóa ô mật khẩu sau gửi. Luồng trình duyệt với tài khoản thật chờ operator tạo admin; đăng nhập thành công/đổi mật khẩu/đăng xuất đã được kiểm trong bộ tích hợp bằng tài khoản tổng hợp.
