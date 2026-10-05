# VN Digital Trust — Tài liệu hiện hành

**Cập nhật:** 2026-10-05

## Baseline v0.1 hiện tại: kỹ thuật và quản lý rủi ro

1. [Quyết định phạm vi kỹ thuật](scope/technical-first-scope-v0.1.md) — mục tiêu, các domain và ranh giới.
2. [Technical Requirements](requirements/requirements-technical-v0.1.md) — chức năng, ràng buộc và acceptance scenarios.
3. [Technical Use Cases](use-cases/use-cases-technical-v0.1.md) và [sơ đồ PlantUML](use-cases/use-cases-technical-v0.1.puml) — người dùng thực hiện gì.
4. [Technical Domain Model](domain-model/domain-model-technical-v0.1.md) và [sơ đồ PlantUML](domain-model/domain-model-technical-v0.1.puml) — các đối tượng, quan hệ và bất biến.

Prototype hiện tập trung vào inventory → risk scenario/evaluation → control/evidence → gap/treatment → retest/report cho **một SME trên một deployment**.

## Tài liệu lịch sử

Các file trong [research](research/), [Requirements Discovery trước đây](requirements/requirements-discovery-v0.1.md), [Use Cases trước đây](use-cases/use-cases-v0.1.md) và [Domain Model trước đây](domain-model/domain-model-v0.1.md) được giữ làm lịch sử nghiên cứu hướng pháp lý. Chúng không phải baseline triển khai kỹ thuật v0.1 và không được diễn giải là quy định pháp luật đã được kiểm chứng.

## Bước thiết kế tiếp theo

Chọn một phương pháp đánh giá likelihood/impact có tiêu chí rõ, một số control mẫu và test fixture ABC Trading; kiểm thử kết quả lặp lại, sự khác nhau giữa thiếu evidence và control thất bại, và việc giữ lịch sử sau retest. Sau đó mới chốt architecture và database.
