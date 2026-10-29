# Quản lý người dùng và phân quyền VDT local — v0.1

Ngày cập nhật: **2026-10-26**, Asia/Bangkok. Phạm vi: quản trị tài khoản trong prototype Bước 06. **Trạng thái triển khai và kiểm tra cuối: DEPLOYED_LOCAL — https://localhost:8443/admin/users.**

Trang quản trị: **https://localhost:8443/admin/users**. Dùng tài khoản quản trị bạn đã tạo; không cần chạy lại lệnh bootstrap. Image và dữ liệu Docker tiếp tục nằm trong thư mục dự án ở ổ D theo [biên bản lưu trữ](docker-storage-v0.1.md).

Người dùng đã báo cáo tạo admin, đăng nhập, đổi mật khẩu và thử sai năm lần dẫn đến thông báo tạm khóa 15 phút đều hoạt động. Đây là xác nhận sử dụng trực tiếp của người dùng; chưa ghi nhận họ kiểm tra đăng xuất hoặc tự mở khóa sau khi chờ đủ 15 phút.

## 1. Mở trang quản trị

1. Mở Docker Desktop và đợi môi trường local sẵn sàng.
2. Đăng nhập tại **https://localhost:8443** bằng tài khoản quản trị hiện tại.
3. Mở **https://localhost:8443/admin/users**. Trang có ba mục: **Người dùng**, **Vai trò & phạm vi**, **Nhật ký**.

Nếu ứng dụng đang dừng, mở PowerShell trong thư mục dự án và khởi động:

```powershell
Set-Location "D:\Projects\vn-digital-trust"
docker compose --env-file .runtime/local.env -f lab/local/compose.yaml --profile app up -d db app proxy
```

Tài khoản quản trị chỉ quản lý người dùng, tổ chức và cấp quyền. Nó không tự có quyền đọc bằng chứng hoặc đánh giá nghiệp vụ.

## 2. Tạo một tài khoản

1. Trong **Người dùng**, chọn **+ Tạo tài khoản**.
2. Nhập **Tên đăng nhập**, **Tên hiển thị**, chọn chi nhánh phù hợp và giữ **Cho phép đăng nhập** nếu tài khoản cần hoạt động.
3. Điền **Lý do thay đổi**, rồi chọn **Tạo tài khoản**.

Hồ sơ và chi nhánh chưa cấp quyền truy cập. Tài khoản mới cần mật khẩu tạm và vai trò phù hợp ở hai bước tiếp theo.

## 3. Đặt mật khẩu tạm

1. Chọn tài khoản vừa tạo trong danh sách.
2. Trong **Mật khẩu tạm**, nhập mật khẩu mới hai lần và lý do cấp mật khẩu.
3. Chọn **Đặt mật khẩu tạm**.

Mật khẩu cần ít nhất 12 ký tự, không phổ biến và không chỉ gồm số. Giao mật khẩu trực tiếp qua kênh riêng cho đúng người nhận; không ghi vào ô lý do, nhật ký, báo cáo hay cuộc trò chuyện. Giao diện không cung cấp chức năng xem lại mật khẩu đã lưu.

Lần đăng nhập bằng mật khẩu tạm yêu cầu người dùng đổi sang mật khẩu riêng trước khi thao tác. Trong thời gian đó, các API quản trị/nghiệp vụ bị chặn. Việc đặt lại mật khẩu cũng thu hồi toàn bộ phiên cũ của tài khoản.

Để đổi mật khẩu của chính bạn, mở **Tài khoản của tôi** và dùng phần đổi mật khẩu cá nhân. Trang quản trị chặn tự đặt lại mật khẩu cho tài khoản đang dùng.

## 4. Cấp vai trò và phạm vi

Mở **Vai trò & phạm vi**, chọn người dùng, vai trò, thời điểm bắt đầu và lý do. Chọn ngày hết hạn khi quyền chỉ cần tạm thời, rồi bấm **Cấp quyền**.

| Vai trò | Phạm vi trong giao diện hiện tại | Ý nghĩa |
| --- | --- | --- |
| Quản trị viên — `VDT_ADMIN` | Toàn tổ chức; không chọn chi nhánh | Quản lý tài khoản và cấp quyền. Không tự được đọc bằng chứng hoặc đánh giá. |
| Security — `VDT_SECURITY` | Chọn rõ ít nhất một chi nhánh | Lưu phân quyền vận hành cho đúng chi nhánh; các luồng bằng chứng vẫn đang triển khai. |
| Risk Owner — `VDT_RISK_OWNER` | Chọn rõ ít nhất một chi nhánh | Lưu phân quyền rủi ro theo chi nhánh; phê duyệt ưu tiên cần workflow nghiệp vụ riêng. |
| Reviewer — `VDT_REVIEWER` | Chưa mở lựa chọn trên UI | Cần đợt đánh giá có thật, được giao cụ thể và có ngày hết hạn. Chức năng chọn đợt đánh giá sẽ mở cùng phần đánh giá. |

Thời gian nhập theo múi giờ máy. Quyền chưa đến ngày bắt đầu hoặc đã hết hạn không được dùng. Nếu quyền quản trị của người cấp có ngày hết hạn, họ không thể cấp quyền vô thời hạn hoặc vượt quá hạn quản trị đó.

Chi nhánh trong hồ sơ dùng để mô tả người dùng; phạm vi tại lượt cấp quyền mới xác định giới hạn của grant. Danh mục quyền giữ đủ `evidence.verify`, `evidence.read_assigned` cho Security/Reviewer và `risk.priority_approve` cho Risk Owner; các quyền này không tự mở API nghiệp vụ chưa triển khai.

## 5. Chỉnh sửa, khóa và thu hồi

**Sửa hồ sơ hoặc khóa tài khoản:** chọn người dùng, thay đổi thông tin; bỏ **Cho phép đăng nhập** để khóa, ghi lý do rồi lưu. Khóa tài khoản làm các phiên hiện có mất hiệu lực. Bật lại tài khoản cho phép đăng nhập mới; không phục hồi phiên cũ.

**Thu hồi một lượt cấp quyền:** trong **Vai trò & phạm vi**, chọn thu hồi ở lượt cấp quyền tương ứng, nhập lý do rồi xác nhận. Phần còn lại của hồ sơ được giữ. Quyền được kiểm lại từ dữ liệu hiện hành khi thao tác; một phiên đã đăng nhập không giữ được quyền vừa thu hồi.

Hệ thống chặn tự khóa tài khoản đang sử dụng và thao tác làm mất quản trị viên cuối cùng còn hoạt động, có mật khẩu sử dụng được và đã hoàn tất yêu cầu đổi mật khẩu tạm. Các lượt cấp/thu hồi và lịch sử sửa hồ sơ được giữ để truy vết.

## 6. Xem nhật ký và xử lý xung đột

Mở **Nhật ký** để xem thời gian, người thực hiện, thao tác và kết quả, với sự kiện mới nhất ở đầu. Dùng **Xem thêm sự kiện** khi có trang tiếp theo. Mật khẩu và token không được đưa vào nhật ký, lịch sử hoặc kết quả lưu để chống gửi trùng.

| Tình huống | Cách tiếp tục |
| --- | --- |
| Phiên hết hạn hoặc bị thu hồi | Đăng nhập lại. |
| Đang dùng mật khẩu tạm | Về **Tài khoản của tôi**, đổi mật khẩu rồi mở lại trang quản trị. |
| Chưa có quyền hoặc quyền hết hạn | Nhờ quản trị viên còn quyền kiểm tra lượt cấp quyền. |
| Hồ sơ hoặc dữ liệu liên quan đã thay đổi | Tải bản mới, kiểm tra lại thay đổi rồi lưu; hệ thống không tự ghi đè bản mới hơn. |
| Ngày hết hạn hoặc phạm vi không hợp lệ | Sửa thông tin theo thông báo; không dùng định danh đối tượng tự nhập để thay thế dữ liệu thật. |
| Dịch vụ chưa sẵn sàng | Kiểm tra Docker Desktop và trạng thái app/proxy/db. |

## 7. Hồ sơ kỹ thuật và kiểm thử

Request đi qua Reverse proxy/TLS, xác thực phiên và kiểm quyền hiện hành. Mỗi lần ghi có CSRF, mã chống gửi trùng, lý do và phiên bản phụ thuộc; sửa/thu hồi/đặt lại mật khẩu còn đối chiếu phiên bản tài nguyên. Authorization guard giữ kiểm quyền và mutation trong cùng giao dịch; kiểm lại quyền/hạn trước khi hoàn tất. Mutation, lịch sử, audit và kết quả chống gửi trùng được ghi nguyên tử.

Migration `0003_access_runtime` thêm cờ vận hành `password_change_required` vào `app_user`, mặc định `false` để giữ hành vi tài khoản đã có. Session DTO của thiết kế Bước 05 giữ nguyên; trạng thái yêu cầu đổi mật khẩu được truyền bằng header `X-VDT-Password-Change-Required`. Không sửa tài liệu thiết kế đóng băng.

| Kiểm tra của mốc 2026-10-26 | Kết quả thực tế |
| --- | --- |
| Unit/contract và hash nguồn | **143/143 đạt** |
| API quản trị trên PostgreSQL tạm, bằng tài khoản runtime `vdt_app` | **27/27 đạt** |
| Hồi quy đăng nhập | **22/22 đạt** |
| Giao diện trên trình duyệt với dữ liệu tổng hợp riêng | **12/12 kiểm tra thủ công bằng tài khoản tổng hợp đạt** |
| Cập nhật lab thật và giữ tài khoản quản trị hiện có | **Đạt: giữ nguyên 1 tài khoản/1 lượt cấp quyền và thông tin xác thực; 16/16 database, 12/12 HTTPS auth, 11/11 HTTPS quản trị** |

Cách chạy lại nằm trong [hướng dẫn local](../../lab/local/README.md). Bộ quản trị chỉ chấp nhận database tạm `testdb`, không dùng mật khẩu thật của operator. Tệp credential phục vụ browser QA nằm riêng trong `.runtime/checks`, không phải báo cáo công khai và phải được dọn sau kiểm tra.

Hồ sơ chi tiết: [API quản trị](access-checks-v0.1.json), [kiểm tra trình duyệt](access-browser-checks-v0.1.json), [cập nhật lab và bảo toàn tài khoản](access-deployment-v0.1.json). [Ảnh máy tính](access-preview-desktop-v0.1.png) và [ảnh màn hình nhỏ](access-preview-mobile-v0.1.png) sử dụng tài khoản tổng hợp trên database tạm.

Metadata người dùng lấy lần thay đổi công khai mới nhất, kể cả đăng nhập/đổi mật khẩu vì các thao tác này tăng phiên bản tài khoản. Phạm vi đối tượng chỉ được chấp nhận khi inventory có Scope đầy đủ, hợp lệ; mọi chiều được chọn phải có quan hệ đã xác thực. Nhật ký phân trang theo thời điểm và định danh để không làm mất sự kiện mới.

## 8. Giới hạn của mốc này

- Quản trị viên theo phạm vi toàn tổ chức; cấp ADMIN giới hạn chi nhánh bị từ chối, không được tự mở rộng thành quyền toàn tổ chức.
- UI cấp Security/Risk Owner theo chi nhánh. Cấp theo đối tượng cần dữ liệu inventory đã xác thực; không dùng UUID giả để lấp chỗ trống.
- Chưa mở Reviewer UI, quản lý đợt đánh giá hoặc workflow phê duyệt nghiệp vụ.
- Chưa mở upload, scanner/job, đánh giá/rủi ro/review/retest/report hay CRM local. API chưa triển khai tiếp tục trả trạng thái chưa sẵn sàng sau kiểm tra phiên; người dùng đang dùng mật khẩu tạm phải đổi mật khẩu trước.
- Cấu hình phiên VDT local không thay thế năm trường `AUTH-CRM-01`. FLOW-01…10, T01–T24 và VALID-G-01 vẫn **NOT_RUN**. Chưa có bằng chứng CRM, hiệu chuẩn hoặc phê duyệt SME; Bước 06 vẫn **IN_PROGRESS**.
