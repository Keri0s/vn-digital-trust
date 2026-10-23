# Bước 05 — Công nghệ, dữ liệu và API v0.1

**Hoàn tất thiết kế:** 2026-10-21 (Asia/Bangkok). Bước 06 **NOT_STARTED**.

## Nên đọc theo thứ tự

| Tài liệu | Nội dung |
| --- | --- |
| [Quyết định công nghệ](technology-decisions-v0.1.md) | Django/DRF, PostgreSQL 17, Caddy, kho tệp riêng và worker tuần tự; lý do và giới hạn tài nguyên. |
| [Mô hình dữ liệu](data-model-v0.1.md) và [DDL](schema-v0.1.sql) | 106 bảng gồm bảng nghiệp vụ, phiên bản và liên kết; khóa, trạng thái và lịch sử bất biến. |
| [Hợp đồng API](api-contract-v0.1.md) và [OpenAPI](openapi-v0.1.yaml) | 92 đường dẫn, 123 thao tác; quyền, validation, lỗi, retry và concurrency. |
| [Lưu trữ và giao dịch](storage-transactions-v0.1.md) | Upload, xác minh, commit, crash/reconciliation, report as_of, backup/restore. |
| [Cấu hình và seed](configuration-v0.1.md) | [Mẫu cấu hình](config-template-v0.1.json), [RBAC seed](rbac-seed-v0.1.json) và các điều kiện trước lab. |
| [Truy vết](traceability-v0.1.md) | NOTE-01…10, SC-01/02, FLOW-01…10 và yêu cầu thiết kế. |
| [Biên bản kiểm tra](validation-v0.1.md) | Kết quả kiểm tra tĩnh, sơ đồ, đầu vào giữ nguyên và việc cần kiểm chứng ở bước 06. |

## Sơ đồ

| Sơ đồ | Xem ảnh | Nguồn |
| --- | --- | --- |
| Context, scope và RBAC | [SVG](erd-context-access-v0.1.svg) · [PNG](erd-context-access-v0.1.png) | [PlantUML](erd-context-access-v0.1.puml) |
| Evidence, criteria và control assessment | [SVG](erd-evidence-assessment-v0.1.svg) · [PNG](erd-evidence-assessment-v0.1.png) | [PlantUML](erd-evidence-assessment-v0.1.puml) |
| Risk, decisions, treatment và report | [SVG](erd-risk-decisions-v0.1.svg) · [PNG](erd-risk-decisions-v0.1.png) | [PlantUML](erd-risk-decisions-v0.1.puml) |
| Upload qua proxy/TLS và policy gate | [SVG](upload-sequence-v0.1.svg) · [PNG](upload-sequence-v0.1.png) | [PlantUML](upload-sequence-v0.1.puml) |

ERD chọn các bảng và quan hệ chính để đọc được; từ điển dữ liệu và SQL chứa toàn bộ bảng, khóa ghép và bảng liên kết. Mở SVG để phóng to các nhãn.

## Bốn lưu ý 3.1–3.4 đã được đưa vào thiết kế

1. Upload multipart đi qua reverse proxy/TLS và policy gate; kiểm lại quyền, expiry và dependencies trước commit.
2. Seed hợp nhất quyền từ lab fixture và FLOW overlay, gồm evidence.verify/evidence.read_assigned cho Security và Reviewer theo scope, risk.priority_approve cho Risk Owner.
3. Storage state tách verification; status/score_determined tách assessment_mode/review_outcome. Với control không có điểm RM, score_determined=false đi cùng score_applicability=NOT_APPLICABLE.
4. AUTH-CRM-01 có challenge_ttl_seconds, max_attempt_limit, session_idle_timeout_seconds, rp_id, allowed_origins; giá trị thực còn null/TO_SET_BEFORE_LAB. 120/5/900 chỉ là ví dụ.

## Giới hạn và bước tiếp theo

Đây là bộ thiết kế để triển khai. SQL/API chưa được chạy với PostgreSQL/app. FLOW-01…10, T01–T24 và VALID-G-01 **NOT_RUN**; A/B chưa điền, chưa có CRM evidence hoặc hiệu chuẩn SME. MF-03/MF-04 vẫn NOT_RANKED và chưa được SME phê duyệt ưu tiên.

Bước 06 cần chốt cấu hình/môi trường, pin bản vá, triển khai migration/seed/service, kiểm quyền và bất biến bằng giao dịch thật, kiểm fault/restore, đo tài nguyên rồi chạy các ca đã được phép. Bộ tài liệu này không tự khởi động bước 06. Trạng thái chung nằm tại [kế hoạch §28](../planning/execution-plan-v0.1.md#28-kết-quả-bước-05--thiết-kế-v01-2026-10-21).
