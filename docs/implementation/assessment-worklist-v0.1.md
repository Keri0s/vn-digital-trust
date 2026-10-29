# Đợt đánh giá và giao Reviewer — prototype local

Ngày 2026-10-26. Mốc Bước 06 này đã triển khai tại `https://localhost:8443/assessments` và mục cấp quyền ở `https://localhost:8443/admin/users`.

Sửa lỗi điều hướng ngày 2026-10-26: phiên đăng nhập trước đó chỉ trả ba quyền quản trị, khiến Security/Risk Owner/Reviewer bị ẩn nút và chuyển về trang tài khoản dù API domain đã có quyền đúng. Phiên hiện trả thêm các quyền điều hướng đánh giá đang có hiệu lực; API vẫn kiểm quyền, scope và assignment độc lập dưới authorization guard. Trang tài khoản hiển thị hướng dẫn khi chưa có quyền đánh giá. Đã tải lại phiên người dùng đang mở, thấy nút **Đợt đánh giá**, bấm vào và xác nhận form **Đợt mới** tải được cùng chi nhánh đã cấp. Không tạo đợt thử trong database lab.

Kiểm chứng bản sửa: [26/26 assessment và navigation](assessment-navigation-checks-v0.1.json), [22/22 auth](auth-checks-assessment-navigation-v0.1.json), [143/143 unit](unit-checks-assessment-navigation-v0.1.json). Bộ auth đã cập nhật kỳ vọng: Admin nhận 403 ở assessment đã triển khai; scenario chưa triển khai vẫn trả 503. Ảnh giao diện: [trang đánh giá](assessment-navigation-fixed-v0.1.png), [form tạo đợt](assessment-form-fixed-v0.1.png).

## Tên chi nhánh và hồ sơ consultant — 2026-10-26

Đã sửa cột **Chi nhánh** hiện UUID với Reviewer/Risk Owner: trước đây tên chỉ được tải từ dữ liệu tạo đợt dành cho `assessment.run`. Các vai trò chỉ đọc không gọi được nguồn đó. Giao diện hiện lấy tên và mã chi nhánh thật bằng API phụ trợ, chỉ cho các đợt người dùng đang được phép xem:

- `GET /api/v1/assessments/display-context`: danh sách phân trang thông tin hiển thị theo quyền hiện hành.
- `GET /api/v1/assessments/{id}/display-context`: tên/mã/trạng thái chi nhánh, quyền trên chính đợt đó và thời hạn truy cập thẩm định.

API giữ nguyên DTO `Assessment` của Bước 05. Hai endpoint phụ trợ dùng cùng kiểm phiên, tổ chức, phạm vi và lượt giao việc với API đọc đợt; không mở danh mục chi nhánh toàn tổ chức cho Reviewer. Quyền được kiểm lại trước khi trả kết quả; ngoài phạm vi trả 404, không có quyền trả 403, chưa đăng nhập trả 401. Tên chi nhánh vẫn đọc được khi chi nhánh đã ngừng hoạt động, có nhãn phân biệt.

Mỗi dòng đã có **Mở hồ sơ**. Hồ sơ đọc dữ liệu thật gồm mã/tên, chi nhánh, trạng thái, thời điểm cập nhật, số kịch bản, quyền hiện hành và hạn truy cập của Reviewer. Nếu chưa có kịch bản, trang nói rõ cần bổ sung kịch bản, bằng chứng và bản kết quả trước khi gửi thẩm định. Không có nút kết luận giả hoặc bằng chứng giả.

Theo thiết kế Bước 05, consultant kiểm tra bằng chứng được giao, yêu cầu bổ sung khi cần và xác nhận/phản biện một bản kết quả do người khác lập. Quyết định phải gắn bản kết quả cụ thể, có lý do và giữ lịch sử gốc. **Hiện lab mới có tạo đợt, giao quyền và xem hồ sơ; mở bằng chứng, yêu cầu bổ sung và gửi kết luận thẩm định chưa được triển khai.** Cần hoàn thiện inventory/context/scenario, bằng chứng và kết quả tự đánh giá trước khi nối luồng gửi/nhận thẩm định.

Kiểm chứng bản này: [39/39 assessment](assessment-details-checks-v0.1.json), [143/143 unit](unit-checks-assessment-details-v0.1.json); kiểm tra cú pháp Python và JavaScript đạt. Đã build và cập nhật app local, tải lại phiên consultant đang mở và bấm **Mở hồ sơ** trên đợt do người dùng tạo: chi nhánh hiện **Trụ sở HCM — giả lập (BR-HCM)**, đúng vai trò và thời hạn được giao. [Ảnh hồ sơ thực tế](assessment-detail-branch-v0.1.png). Không gửi form tạo/sửa dữ liệu trong phiên người dùng khi kiểm tra giao diện.

Kiểm tra khi tiếp tục công việc: Docker đang tắt nên đã khởi động lại Docker Desktop và ba thành phần lab bằng image hiện có, không build/pull thêm. Database vẫn có **1 đợt**; dấu đối chiếu `id + version + api_payload` trước/sau giống nhau (`979ca7fae3802106774bd6df60968986`). Bảy file mã nguồn/kiểm thử thay đổi khớp SHA-256 trong báo cáo unit. Trình duyệt mở `https://localhost:8443/assessments` thành công và chuyển về đăng nhập do phiên cũ không còn; không đăng nhập thay người dùng. Database kiểm thử tạm của project `vdt-assessment-test` đã được dọn riêng.

## Cách dùng

1. Đăng nhập bằng tài khoản được cấp `VDT_SECURITY` tại một chi nhánh và mở **Đợt đánh giá** từ trang tài khoản.
2. Tạo mã, tên, chọn chi nhánh và ghi lý do. Đợt mới ở trạng thái `OPEN`, chưa gắn kịch bản. Quyền `assessment.run` và chi nhánh được kiểm ngay trước khi ghi.
3. Đăng nhập tài khoản quản trị, vào **Người dùng & phân quyền → Vai trò & phạm vi**, chọn người dùng và vai trò **Người thẩm định**, chọn chính đợt đang mở và đặt hạn truy cập.
4. Người thẩm định đăng nhập, mở **Đợt đánh giá → Mở hồ sơ** để xem thông tin, phạm vi và thời hạn. Chỉ đợt được giao trong thời hạn còn hiệu lực xuất hiện. Việc cấp vai trò không cấp thêm quyền tạo đợt. Các thao tác thẩm định được mô tả ở trên còn đang triển khai.

Admin chỉ xem danh sách chọn đợt gồm mã, tên, phiên bản, phạm vi và trạng thái qua API phụ trợ `/api/v1/admin/assessments`; không có quyền đọc chi tiết `/api/v1/assessments/{id}`. Đợt đánh giá và scope nằm trong các bảng domain hiện có. Bản ghi tạo có lịch sử bất biến, nhật ký và khóa idempotency; `scenario_ids` ban đầu rỗng theo hợp đồng Bước 05. Bản cập nhật gắn kịch bản, inventory, xác minh bằng chứng và review quyết định sẽ triển khai ở mốc sau.

## Kiểm chứng mốc tạo/giao đợt ban đầu (lịch sử)

- 11/11 kiểm tra tích hợp trên PostgreSQL `testdb` tmpfs riêng: quyền Admin/Security/Reviewer, chi nhánh ngoài phạm vi, tạo đợt, gửi lại cùng khóa, selector quản trị và giao Reviewer.
- `python manage.py check`: không lỗi cấu hình.
- Database lab trước và sau cập nhật: **2 tài khoản, 2 lượt cấp quyền, 0 đợt đánh giá, 2 chi nhánh**. Không tạo dữ liệu đánh giá thử trong database thật.
- Trang và API mới phản hồi qua TLS local: health 200; trang đánh giá chuyển về đăng nhập và API trả 401 khi chưa xác thực.
- Backup trước triển khai: `D:\Projects\vn-digital-trust\.runtime\backups\vdt-before-assessment-20261026.dump`, 472604 byte; `pg_restore -l` đọc được. Chưa thử phục hồi.

Để lặp lại kiểm thử trên database tạm: chạy `docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.assessment-test.yaml run --rm check`, rồi `docker compose` với đúng hai file đó và `down`. Không dùng `down -v` trên project lab thật.
