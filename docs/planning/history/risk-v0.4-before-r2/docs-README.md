# VN Digital Trust — Tài liệu hiện hành

**Cập nhật:** 2026-10-11

## Baseline v0.1 hiện tại: kỹ thuật và quản lý rủi ro

1. [Quyết định phạm vi kỹ thuật](../../../scope/technical-first-scope-v0.1.md) — mục tiêu, các domain và ranh giới.
2. [Technical Requirements](../../../requirements/requirements-technical-v0.1.md) — chức năng, ràng buộc và acceptance scenarios.
3. [Technical Use Cases](../../../use-cases/use-cases-technical-v0.1.md) và [sơ đồ PlantUML](../../../use-cases/use-cases-technical-v0.1.puml) — người dùng thực hiện gì.
4. [Technical Domain Model](../../../domain-model/domain-model-technical-v0.1.md) và [sơ đồ PlantUML](../../../domain-model/domain-model-technical-v0.1.puml) — các đối tượng, quan hệ và bất biến.
5. [Phạm vi lab và dữ liệu giả lập](../../lab-scope-and-fixtures-v0.1.md), [JSON fixture](../../lab-fixtures-v0.1.json) — LAN/VPN, hai chi nhánh trong một công ty, tài khoản/role, dữ liệu và hai scenario. Đã chốt mật khẩu + WebAuthn cho demo CRM; chưa triển khai lab.
6. [Phương pháp risk nhiều yếu tố RM-01 v0.4 — đang review](risk-method-v0.4.md), [fixture tính toán](../../verification/risk-method-fixtures-v0.4.json), [control/evidence CE-01 v0.1](../../control-evidence-v0.1.md), [ca kiểm thử TC-01 v0.1](../../control-test-cases-v0.1.md) — đầu ra thiết kế bước 02; chưa có evidence hay kiểm thử CRM thực tế.

Prototype hiện tập trung vào inventory → risk scenario/evaluation → control/evidence → gap/treatment → retest/report cho **một SME trên một deployment**.

## Tài liệu lịch sử

Các file trong [research](../../../research), [Requirements Discovery trước đây](../../../requirements/requirements-discovery-v0.1.md), [Use Cases trước đây](../../../use-cases/use-cases-v0.1.md) và [Domain Model trước đây](../../../domain-model/domain-model-v0.1.md) được giữ làm lịch sử nghiên cứu hướng pháp lý. Chúng không phải baseline triển khai kỹ thuật v0.1 và không được diễn giải là quy định pháp luật đã được kiểm chứng.

## Bước thiết kế tiếp theo

Đọc [Kế hoạch thực hiện 6 bước](execution-plan-v0.1.md) trước khi tiếp tục ở bất kỳ chat nào. **Bước 01 COMPLETE; bước 02 IN_PROGRESS** để review công thức nhiều yếu tố RM-01 v0.4 theo yêu cầu ngày 2026-10-10. Xem mục 16 của kế hoạch. RM-01 v0.1/v0.2/v0.3 và bàn giao mục 13–15 là lịch sử; bước 03–06 chưa bắt đầu. Các sửa đổi v0.4 về UNKNOWN, phép tính chính xác, hiển thị và cách diễn giải hệ quả công thức đã được người dùng đồng ý áp dụng. Review thiết kế MF-03/MF-04 đã được trợ lý thực hiện ngày 2026-10-11: cả hai HIGH, đề xuất MF-04 trước khi tiền điều kiện có độ khả dĩ tương đương và ưu tiên hậu quả rộng hơn; thứ tự doanh nghiệp thực tế vẫn chưa xác định. Việc còn lại là kiểm tra G bởi hai người hoặc chốt phạm vi kiểm tra này. [Báo cáo độ nhạy v0.4](risk-method-review-v0.4.md) có kết quả số học; chấm độc lập vẫn NOT_RUN.

Thứ tự: scenario/phạm vi → phương pháp risk và control/evidence → luồng xử lý → kiến trúc → công nghệ/DB/API → prototype và kiểm chứng. Chỉ chuyển bước khi có đầu ra đáp ứng điều kiện hoàn thành trong kế hoạch.

Initial access là ví dụ đầu; exfiltration là ca kiểm tra khả năng mở rộng mô hình. Atomic Red Team dự kiến dùng để kiểm chứng ở bước 06; Caldera tùy chọn sau các kiểm thử nhỏ hoặc để v0.2+. Tài liệu thiết kế hiện có chưa chứng minh prototype đã hoạt động.
