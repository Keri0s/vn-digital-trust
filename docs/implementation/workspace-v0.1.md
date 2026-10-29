# Chuẩn bị hồ sơ và giao kịch bản — 2026-10-27

Mốc này đã **DEPLOYED_LOCAL** tại `https://localhost:8443/workspace`, bổ sung hệ thống, tài sản, dữ liệu, bối cảnh và kịch bản cho đợt đánh giá. Bước 06 vẫn **IN_PROGRESS**. Cập nhật giữ nguyên 4 tài khoản, 4 lượt cấp quyền và 1 đợt đánh giá; xem [biên bản triển khai](workspace-deployment-v0.1.json).

## Thao tác trên giao diện

1. Đăng nhập bằng tài khoản **Security** có quyền ở chi nhánh cần làm. Vào **Đợt đánh giá → Chuẩn bị hệ thống & kịch bản** (`https://localhost:8443/workspace`). Admin quản lý quyền; Admin không tự có quyền nghiệp vụ này.
2. Ở **Hệ thống & tài sản**, chọn chi nhánh, rồi chọn loại hồ sơ: Hệ thống, Tài sản hoặc Dữ liệu. Nhập mã, tên, người phụ trách nếu đã biết, nguồn thông tin và lý do khai báo. Với từng thuộc tính, chọn **Đã biết** và nhập nội dung có nguồn, hoặc **Chưa xác định** và ghi lý do. Không dùng giả định làm bằng chứng đã xác minh.
3. Tạo các tài sản/dữ liệu cần thiết, chọn hệ thống liên quan. Liên kết đã lưu được giữ; mốc này chưa hỗ trợ tháo liên kết hoặc chuyển hồ sơ sang chi nhánh khác.
4. Chọn **Bối cảnh & kịch bản**. Chọn ít nhất một hệ thống hoặc tài sản đang sử dụng, ghi điều kiện và nguồn, rồi **Lưu bối cảnh**. Bối cảnh giữ nguyên thông tin tại thời điểm lưu.
5. Nhập mã, tên, sự kiện có thể xảy ra, hậu quả, người phụ trách và nguồn của kịch bản. **Lưu bản nháp**, kiểm tra mô tả, ghi lý do và chuyển sang **Đang sử dụng**. Trạng thái này cho phép đưa vào đợt; chưa phải kết luận rủi ro đã được xác minh.
6. Vào **Đợt đánh giá → Mở hồ sơ** của đợt đang mở. Ở **Thêm kịch bản vào đợt**, chọn kịch bản, ghi lý do và lưu. Đợt giữ chính xác phiên bản kịch bản đã chọn.
7. Consultant/Reviewer đăng nhập bằng tài khoản được giao đúng đợt và còn hạn. Mở hồ sơ để đọc sự kiện, hậu quả, nguồn, bối cảnh và phần mở rộng **Hệ thống, tài sản và dữ liệu tại lúc lưu bối cảnh**. Consultant không có form sửa/gắn kịch bản.

Đợt `Test` hiện có của người dùng không được tự thêm dữ liệu mẫu. Người dùng chọn hệ thống và kịch bản phù hợp rồi thêm vào đợt đó. Nếu không thấy liên kết chuẩn bị hồ sơ, kiểm tra đang dùng tài khoản Security và phạm vi chi nhánh của lượt cấp quyền.

## Dữ liệu và quyền

- Mỗi hồ sơ thuộc đúng một chi nhánh ở mốc này. Liên kết hệ thống–tài sản được cập nhật nhất quán hai chiều và tăng phiên bản. Quan hệ chỉ được bổ sung.
- Ghi dữ liệu qua HTTPS/proxy, CSRF, kiểm quyền theo phạm vi, khóa phiên bản, dependency version, idempotency, history và audit trong cùng transaction. Quyền được kiểm lại trước khi hoàn tất; lỗi audit hoặc quyền hết hạn khiến toàn bộ thao tác hoàn tác.
- Bối cảnh lưu bản chụp của inventory; sửa inventory sau đó không đổi bối cảnh. Sửa/chuyển trạng thái kịch bản tạo bản chụp mới. Liên kết với đợt giữ bản chụp cụ thể; không tự chuyển sang bản mới.
- Reviewer chỉ đọc dữ liệu trong hồ sơ đợt được giao, theo phạm vi và thời hạn đang có hiệu lực. Không cấp quyền xem toàn bộ danh mục qua việc được giao một đợt.
- Chưa có vendor/data-flow trong giao diện. API từ chối nội dung này thay vì bỏ qua. Nguồn `EVIDENCE_REVISION` cũng chưa mở.

## Kiểm chứng

- Workspace PostgreSQL tạm: **60/60 đạt**, gồm schema, nguồn/UNKNOWN, quyền, phiên bản, gửi trùng/cạnh tranh, bất biến, hồ sơ Reviewer, thu hồi quyền, rollback và migration downgrade guard. Một kiểm tra là chuẩn bị tài khoản browser tổng hợp; không có bằng chứng CRM.
- Hồi quy: **143/143 unit**, **39/39 assessment**, **22/22 đăng nhập**.
- Browser QA dùng `https://localhost:8444`, database tạm riêng và tài khoản tổng hợp. Kết quả thao tác, ảnh và kiểm tra triển khai được lưu riêng, không dùng mật khẩu thật của người dùng.
- Sau triển khai: **16/16 database, 12/12 HTTPS nền, 11/11 HTTPS workspace** đạt. Các tài nguyên giao diện đang phục vụ khớp nội dung nguồn đã kiểm thử. Đã xác minh 15 nhóm dữ liệu giữ nguyên trước/sau migration; backup nằm ở `.runtime/backups/vdt-before-workspace-20261027.dump`, kiểm danh mục archive đọc được nhưng chưa thử phục hồi toàn bộ.
- Xem [bổ sung hợp đồng API](workspace-api-addendum-v0.1.md), [kết quả workspace](workspace-checks-v0.1.json), [kết quả browser](workspace-browser-checks-v0.1.json).

## Phần tiếp theo

Nộp/đọc bằng chứng qua Reverse proxy và Policy gate, scanner/job, xác minh bằng chứng, tính kết quả đánh giá và yêu cầu thẩm định. **Chưa có** nút yêu cầu bổ sung hoặc gửi kết luận consultant ở mốc này. FLOW-01…10, T01–T24, VALID-G-01 và nghiệm thu CRM vẫn **NOT_RUN**.
