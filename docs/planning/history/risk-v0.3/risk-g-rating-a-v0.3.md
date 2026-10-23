# Phiếu chấm G độc lập A — v0.3

**Trạng thái:** NOT_RUN; đây là phiếu trống. Không có điểm đã điền.

Dùng [rubric v0.3 mục 4](risk-method-v0.3.md). Chấm trước khi xem phiếu người kia; không dùng báo cáo điểm/đáp án từ người điều phối. Những mô tả SYN dưới đây là cùng một gói thông tin tổng hợp, không phải kiểm chứng CRM. Có quyền chọn UNKNOWN và yêu cầu thêm dữ liệu.

- Người chấm A: ____________________
- Ngày/giờ: ____________________
- Xác nhận chưa xem điểm của người kia: ____________________

## GR-01

Scope liệt kê đủ login thường, đường tương tác thay thế, enrollment, recovery và credential lifecycle. Gói evidence tổng hợp SYN-01 mô tả tiêu chí bắt buộc đều đã được xác minh đạt trên từng đường; chưa ghi hạn chế phụ. Đây là giả định bài chấm, không phải evidence CRM.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________

## GR-02

SYN-02 chỉ có evidence login thường đạt. Danh sách scope có đường recovery và login thay thế nhưng chưa có evidence cho hai đường đó. Không có observation chứng minh bypass.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________

## GR-03

SYN-03 xác minh đúng tiền điều kiện password-only và có phiên nghiệp vụ được cấp; log/quan sát tương ứng đủ, các đường khác đã kiểm. Mục tiêu sự kiện là được cấp phiên trái phép khi chỉ có mật khẩu.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________

## GR-04

SYN-04 xác minh một lớp kiểm soát trên đường khôi phục suy yếu. Một lớp xác minh danh tính độc lập vẫn có hiệu lực: hành vi hiện tại bị chặn, muốn tiếp tục cần sự chấp thuận của người xác minh độc lập mà đối thủ chưa có trong tiền điều kiện. Gói thông tin mô tả cản trở này và test âm hợp lệ; không có bằng chứng đạt được sự kiện.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________

## GR-05

SYN-05 xác minh control của một đường suy yếu. Cản trở còn lại chỉ đòi hỏi điều chỉnh thông thường với năng lực đối thủ đã mô tả, không cần điều kiện độc lập mới. Gói thông tin có test xác minh mức cản trở nhỏ; chưa có observation chứng minh sự kiện/hậu quả đã hoàn tất. Các đường khác được kiểm đầy đủ.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________

## GR-06

SYN-06 có một đường đã chứng minh bypass như GR-03; đường recovery chưa có evidence. Cần giữ cả control failure đã xác minh và phần coverage chưa rõ; không được tự hoàn thiện coverage từ đường bypass.

| path_id | Coverage | g hoặc UNKNOWN | Cản trở còn lại / reason / reference SYN |
| --- | --- | --- | --- |
| Điền từng đường áp dụng | | | |

- G hoặc G_range: ____________________
- Control gap/evidence gap còn lại: ____________________
- Điểm chưa rõ và căn cứ phân biệt g=3/4 nếu liên quan: ____________________
- Thời điểm hoàn tất: ____________________
