# VN Digital Trust — Quyết định phạm vi kỹ thuật v0.1

**Ngày:** 2026-10-05

**Trạng thái:** Quyết định thiết kế cho prototype; chưa phải kết quả kiểm chứng với SME.

## 1. Quyết định

Prototype v0.1 tập trung vào **cybersecurity readiness và quản lý rủi ro kỹ thuật cho một SME**. Luồng chính là:

1. Ghi nhận hệ thống, tài sản, dữ liệu quan trọng và phụ thuộc nhà cung cấp.
2. Mô tả các tình huống rủi ro gắn với hệ thống/tài sản.
3. Đánh giá khả năng xảy ra và tác động theo một phương pháp được ghi rõ.
4. Liên kết rủi ro với các biện pháp bảo vệ (control) và bằng chứng triển khai.
5. Phân biệt thiếu bằng chứng với biện pháp bảo vệ chưa đạt.
6. Ưu tiên xử lý, giao việc, đánh giá lại và báo cáo có thể truy vết.

**Một deployment = một SME.** Nhiều người dùng có quyền khác nhau; consultant có thể review nếu được mời. Prototype dùng dữ liệu giả lập/kiểm soát để đánh giá phương pháp.

## 2. Các domain trong v0.1

| Domain | Câu hỏi nghiệp vụ | Đầu ra chính |
| --- | --- | --- |
| Tổ chức và quyền | Ai được nhập, đánh giá, chấp nhận rủi ro và xem báo cáo? | Hồ sơ tổ chức, tài khoản, vai trò, audit. |
| Hệ thống và tài sản | Doanh nghiệp có những hệ thống/tài sản nào, ai chịu trách nhiệm và chúng phụ thuộc vào đâu? | Inventory và quan hệ system–asset. |
| Bối cảnh dữ liệu/nhà cung cấp | Hệ thống chứa dữ liệu quan trọng nào và dùng dịch vụ bên ngoài nào? | Bối cảnh để đánh giá tác động; chưa suy ra nghĩa vụ pháp lý. |
| Rủi ro | Điều gì có thể xảy ra, ảnh hưởng tới đâu, khả năng và tác động được ước lượng ra sao? | Risk scenario, evaluation, rationale, owner và risk register. |
| Control và bằng chứng | Biện pháp bảo vệ nào được chọn, được triển khai ở đâu, có bằng chứng gì? | Control implementation, evidence và trạng thái kiểm tra. |
| Gap và xử lý | Thiếu biện pháp, biện pháp chưa đạt hay chỉ thiếu bằng chứng? Ai xử lý và khi nào kiểm tra lại? | Gap, treatment decision, task và kết quả đánh giá lại. |
| Báo cáo và lịch sử | Có thể giải thích kết quả và lần theo các thay đổi không? | Risk/readiness report, audit trail và assessment snapshot. |

**Ví dụ xuyên suốt:** ABC Trading dùng CRM để xử lý dữ liệu khách hàng. Một tình huống rủi ro là truy cập trái phép vào CRM. Người dùng đánh giá tác động và khả năng xảy ra với lý do cụ thể; liên kết control MFA và bằng chứng cấu hình. Nếu chưa có bằng chứng, kết quả là **INSUFFICIENT_EVIDENCE**, không tự kết luận MFA chưa bật. Nếu bằng chứng đã xác minh cho thấy MFA tắt, kết quả có thể là **NOT_SATISFIED** và tạo control gap.

## 3. Quan hệ với hướng pháp lý trước đây

- Các tài liệu research và baseline pháp lý trước đây được giữ làm **lịch sử discovery**, không bị viết lại thành phát hiện mới.
- v0.1 không xác định nghĩa vụ pháp lý áp dụng cho một doanh nghiệp, không tính điểm tuân thủ, không tạo hồ sơ nộp cơ quan nhà nước và không cấp chứng nhận.
- Các đối tượng Organization, System, Asset, DataAsset, Vendor, Control, Evidence, Gap và Assessment vẫn hữu ích. RegulatoryRequirement, ApplicabilityRule và RequirementControlMapping không thuộc đường chạy chính của prototype kỹ thuật.
- Một lớp liên kết pháp lý có thể được nghiên cứu sau khi có phạm vi nguồn, cách diễn giải và kết quả mẫu được người có chuyên môn rà soát. Đây là khả năng mở rộng, chưa phải cam kết phiên bản sau.
- Nếu tên đề tài, mục tiêu hoặc tiêu chí chấm điểm đã được giảng viên phê duyệt với phần pháp lý là bắt buộc, thay đổi phạm vi này cần được phản ánh trong đề cương nộp cho giảng viên.

## 4. Nguyên tắc đánh giá rủi ro

- Risk scenario gắn với tài sản/hệ thống và mô tả sự kiện, điểm yếu hoặc điều kiện liên quan, hậu quả và người phụ trách. Một cảnh báo scanner không tự trở thành rủi ro.
- Người đánh giá ghi **likelihood**, **impact**, lý do, thông tin dựa vào và mức tin cậy. Công thức hoặc ma trận xếp hạng phải có version và có thể kiểm thử với đầu vào cố định; chưa đặt ngưỡng tùy tiện trong tài liệu này.
- Mức ưu tiên xử lý dựa trên kết quả rủi ro, tầm quan trọng tài sản và trạng thái control/evidence theo quy tắc công khai. Kết quả sơ bộ có thể được người có quyền review.
- Chấp nhận rủi ro là quyết định xử lý của người được ủy quyền, có lý do và thời điểm. Nó không xóa tình huống rủi ro hoặc biến control chưa đạt thành đã đạt.
- Đánh giá lại tạo bản kết quả mới và giữ lịch sử; không sửa đè kết quả đã được dùng trong báo cáo.

## 5. Giới hạn prototype

Ngoài phạm vi v0.1: full SOC/SIEM, phát hiện mối đe dọa theo thời gian thực, quét tài sản quy mô lớn, pentest tự động, AI tự quyết định rủi ro, GRC enterprise, multi-tenant SaaS và các kết luận pháp lý. Có thể **nhập thủ công** một báo cáo cấu hình, log hoặc scanner làm evidence; người dùng vẫn phải đánh giá nguồn và ý nghĩa của nó.

## 6. Tiêu chí kiểm chứng

Với một SME giả lập, người dùng có thể đi hết luồng từ inventory đến risk register, control/evidence, gap, task, retest và report. Các trường hợp kiểm tra tối thiểu gồm: tài sản thiếu owner; dữ liệu tác động chưa rõ; cùng đầu vào và cùng risk-method version cho cùng kết quả; thiếu bằng chứng khác control thất bại; chấp nhận rủi ro không thay đổi control status; assessment cũ vẫn đọc được sau khi sửa inventory hoặc thay evidence.

Đây là tiêu chí cho prototype, không chứng minh rằng SME thực tế muốn tự đánh giá. Phỏng vấn và thử nghiệm với người dùng vẫn cần để kiểm chứng H3/H4 trong Hypotheses Register.

## 7. Tài liệu hiện hành

- [Requirements kỹ thuật v0.1](requirements-technical-v0.1.md)
- Use cases kỹ thuật v0.1
- Domain model kỹ thuật v0.1

Các file requirements-discovery-v0.1.md, use-cases-v0.1.md và domain-model-v0.1.md mô tả hướng pháp lý trước quyết định này. Chúng không còn là baseline triển khai kỹ thuật hiện tại.
