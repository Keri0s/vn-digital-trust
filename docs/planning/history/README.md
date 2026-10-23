# Lịch sử tài liệu planning

**Cập nhật phân loại:** 2026-10-12. Các tệp ở đây đã được thay thế hoặc là snapshot trước đính chính; không dùng chúng làm phương pháp hiện hành. Quay về [chỉ mục planning](../README.md).

| Thư mục | Tệp giữ lại | Lý do giữ |
| --- | --- | --- |
| [risk-v0.1](risk-v0.1/risk-method-v0.1.md) | 1 phương pháp | Theo dõi xuất phát điểm L×I và đối chiếu IBM |
| [risk-v0.2](risk-v0.2/risk-method-v0.2.md) | Phương pháp + fixture | Theo dõi lựa chọn nhiều yếu tố và các quy tắc đã có từ đầu |
| [risk-v0.3](risk-v0.3/risk-method-v0.3.md) | Phương pháp + fixture + báo cáo + phiếu A/B | Theo dõi cổng impact, range và những bất nhất được v0.4 sửa |
| [risk-v0.4-before-r2](risk-v0.4-before-r2/risk-method-v0.4.md) | Phương pháp + báo cáo + execution plan + docs README | Snapshot trước bổ sung impact_progress và đính chính quyết định cặp MF-03/MF-04 |

Tổng cộng 12 tệp lịch sử gốc; README này là chỉ mục mới. Vẫn giữ nội dung/nhận xét tại thời điểm tạo, kể cả các hạn chế hoặc kết luận đã được sửa về sau. Khi tổ chức lại chỉ cập nhật đường dẫn tương đối. Link tới tài liệu control/lab chưa đổi phiên bản có thể dẫn về bộ hiện hành; snapshot README có thêm link ra ngoài planning tới tài liệu chung của repository. Đây không phải snapshot đầy đủ của toàn bộ repository.

Phiếu G v0.3 trống được giữ như thiết kế rubric cũ; khi chấm mới dùng hai [phiếu v0.4](../review-forms/risk-g-rating-a-v0.4.md). Fixture cũ chỉ tái hiện cách tính cũ, không trộn vào [bộ kiểm tra v0.4](../verification/README.md).

Trước r2 chưa có fixture mới khác cho v0.4: bộ số học chính và phiếu v0.4 giữ nguyên, nên snapshot trước r2 dẫn tới chúng ở verification/review-forms. Không nhân bản thêm các tệp này chỉ để lấp đầy thư mục lịch sử.

## Snapshot r2 trước khi đóng băng thiết kế

[risk-v0.4-r2.zip](risk-v0.4-r2.zip) giữ nguyên các tài liệu hiện hành trước r3, gồm bộ verification có fixture/script/kết quả đúng hash, hai phiếu trống và docs/README.md. Manifest bên trong ghi SHA-256 từng tệp. Một gói thay cho việc tạo thêm nhiều file lịch sử rời; không chứa toàn bộ repository. Giải nén rồi đọc planning/verification/README.md nếu cần tái lập r2. R3 không viết lại nội dung trong gói này.

## Đính chính bước 03 — 2026-10-17

[step03-v0.2-before-r1.zip](step03-v0.2-before-r1.zip) giữ use case, nguồn sơ đồ, hai SVG tuyến tính sai cấu trúc và tài liệu điều phối trước sửa. Đây là lịch sử lỗi để truy vết, không dùng để triển khai. Bản hiện hành và biên bản sửa ở [kế hoạch mục 22](../execution-plan-v0.1.md).
