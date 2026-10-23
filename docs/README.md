# VN Digital Trust — Tài liệu hiện hành

**Cập nhật:** 2026-10-23

Bắt đầu tại [chỉ mục planning](planning/README.md): tài liệu hiện hành, thứ tự đọc, tóm tắt thay đổi và nơi lưu lịch sử.

## Baseline v0.1 hiện tại: kỹ thuật và quản lý rủi ro

1. [Quyết định phạm vi kỹ thuật](scope/technical-first-scope-v0.1.md) — mục tiêu, các domain và ranh giới.
2. [Technical Requirements](requirements/requirements-technical-v0.1.md) — chức năng, ràng buộc và acceptance scenarios.
3. [Technical Use Cases v0.2-r1](use-cases/use-cases-technical-v0.2.md), [activity](use-cases/assessment-flow-v0.2.puml) và [sequence](use-cases/retest-sequence-v0.2.puml) — người dùng thực hiện gì; [ảnh và biên bản kiểm tra](use-cases/diagram-validation-v0.2-r1.md).
4. [Technical Domain Model](domain-model/domain-model-technical-v0.1.md) và [sơ đồ PlantUML](domain-model/domain-model-technical-v0.1.puml) — các đối tượng, quan hệ và bất biến.
5. [Phạm vi lab và dữ liệu giả lập](planning/lab-scope-and-fixtures-v0.1.md), [JSON fixture](planning/lab-fixtures-v0.1.json) — LAN/VPN, hai chi nhánh trong một công ty, tài khoản/role, dữ liệu và hai scenario. Đã chốt mật khẩu + WebAuthn cho demo CRM; chưa triển khai lab.
6. [Phương pháp risk nhiều yếu tố RM-01 v0.4-r3 — đóng băng thiết kế](planning/risk-method-v0.4.md), [fixture tính toán](planning/verification/risk-method-fixtures-v0.4.json), [control/evidence CE-01 v0.1](planning/control-evidence-v0.1.md), [ca kiểm thử TC-01 v0.1](planning/control-test-cases-v0.1.md) — đầu ra thiết kế bước 02; chưa có evidence hay kiểm thử CRM thực tế.
7. [Kiến trúc kỹ thuật v0.1](architecture/architecture-technical-v0.1.md), [sơ đồ container](architecture/container-v0.1.svg), [deployment](architecture/deployment-v0.1.svg), [evidence/decision](architecture/evidence-decision-flow-v0.1.svg) và [biên bản kiểm tra](architecture/diagram-validation-v0.1.md) — đầu ra thiết kế bước 04; chưa triển khai.

8. [Thiết kế công nghệ, dữ liệu và API v0.1](design/README.md) — đầu ra bước 05; gồm ERD/DDL, OpenAPI, storage/transaction, config/RBAC và [biên bản kiểm tra](design/validation-v0.1.md).
9. [Triển khai Bước 06](implementation/README.md) — mã nền và kiểm chứng thực tế, [phương án lab local](implementation/local-crm-lab-plan-v0.1.md), [image/data Docker ở ổ D](implementation/docker-storage-v0.1.md); còn đang thực hiện.

Prototype hiện tập trung vào inventory → risk scenario/evaluation → control/evidence → gap/treatment → retest/report cho **một SME trên một deployment**.

## Tài liệu lịch sử

Các file trong [research](research), [Requirements Discovery trước đây](requirements/requirements-discovery-v0.1.md), [Use Cases trước đây](use-cases/use-cases-v0.1.md) và [Domain Model trước đây](domain-model/domain-model-v0.1.md) được giữ làm lịch sử nghiên cứu hướng pháp lý. Chúng không phải baseline triển khai kỹ thuật v0.1 và không được diễn giải là quy định pháp luật đã được kiểm chứng.

## Tiến độ hiện hành

**Bước 05 COMPLETE về thiết kế v0.1 ngày 2026-10-21; đầu ra và kiểm tra tại [chỉ mục thiết kế](design/README.md), kế hoạch mục 28. Bước 06 IN_PROGRESS theo yêu cầu ngày 2026-10-23 (mục 29).**

Đọc [chỉ mục planning](planning/README.md) và [kế hoạch thực hiện 6 bước](planning/execution-plan-v0.1.md) trước khi tiếp tục ở bất kỳ chat nào. **Bước 01 và bước 02 COMPLETE về thiết kế; bước 03 COMPLETE về thiết kế v0.2-r1, sơ đồ đã được render, đọc kiểm tra và được người dùng xác nhận ngày 2026-10-18 (mục 22–23), bước 04 COMPLETE về thiết kế kiến trúc v0.1 theo mục 25; bước 05 COMPLETE về thiết kế v0.1 theo mục 28; bước 06 IN_PROGRESS theo mục 29.** Bản RM-01 v0.4-r3 giữ profile tính điểm v0.4; bàn giao bước 02 → 03 theo yêu cầu người dùng ngày 2026-10-13 ở mục 20; biên bản đóng thiết kế/VALID-G-01 ở mục 19; mục 13–18 là nhật ký lịch sử. R3 bổ sung cờ xấu đi và mô tả max khi theo dõi impact, khôi phục quy tắc AI/fixture, cập nhật kế hoạch/lab criteria và xác nhận lại nguồn NIST. [Gói tái lập](planning/verification/README.md) có 26 fixture chính và 20 ca impact. [Báo cáo review](planning/verification/risk-method-review-v0.4.md) giữ NOT_RANKED là REVIEWER_DETERMINATION của trợ lý, chưa có xác nhận/đổi của người dùng. Kiểm chứng hai người chấm G chuyển sang **VALID-G-01, bước 06: NOT_RUN**; phiếu vẫn trống, độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng. Đóng thiết kế không đồng nghĩa đã có prototype, evidence CRM hay hiệu chuẩn SME.

Thứ tự: scenario/phạm vi → phương pháp risk và control/evidence → luồng xử lý → kiến trúc → công nghệ/DB/API → prototype và kiểm chứng. Chỉ chuyển bước khi có đầu ra đáp ứng điều kiện hoàn thành trong kế hoạch.

Initial access là ví dụ đầu; exfiltration là ca kiểm tra khả năng mở rộng mô hình. Atomic Red Team dự kiến dùng để kiểm chứng ở bước 06; Caldera tùy chọn sau các kiểm thử nhỏ hoặc để v0.2+. Tài liệu thiết kế hiện có chưa chứng minh prototype đã hoạt động.

