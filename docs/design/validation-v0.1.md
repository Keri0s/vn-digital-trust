# Biên bản kiểm tra thiết kế Bước 05 v0.1

**Ngày:** 2026-10-21 (Asia/Bangkok). **Phạm vi:** STATIC_DESIGN_ONLY. **Kết luận:** bộ thiết kế đáp ứng điều kiện Bước 05 tại kế hoạch §26; Bước 06 vẫn NOT_STARTED.

## 1. Kiểm tra có thể tái lập

[Kết quả JSON](verification/results-v0.1.json) ghi **21/21 kiểm tra tĩnh đạt**, 0 lỗi. [Script](verification/verify-design-v0.1.py) chỉ đọc tài liệu, không mở DB/app hay chạy lab.

| Nhóm | Kết quả thực tế |
| --- | --- |
| OpenAPI 3.1.1 | Cấu trúc hợp lệ; 92 paths, 123 operation IDs duy nhất; local $ref giải được; 6 ví dụ schema hợp lệ. |
| PostgreSQL DDL | Parser đọc 390 statements, 106 tables; transaction có COMMIT; 10 hàm PL/pgSQL parse được. |
| FK | 287 khai báo FK có bảng/cột đích; khóa đích có PK/UNIQUE được khai báo. |
| RBAC/API | Permission của các domain operation thuộc catalog; seed đúng baseline + FLOW + hai extension công khai; user/scope/expiry gốc giữ nguyên. |
| Cấu hình | Năm trường CRM còn null/TO_SET_BEFORE_LAB; ví dụ tách biệt; upload limits 20 MiB file / 64 KiB metadata / 21 MiB request khớp. |
| Đầu vào | SHA-256 của 8 đầu vào trong [input manifest](input-manifest-v0.1.json) không đổi. |
| Tài liệu | Link tệp Markdown cục bộ trong design tồn tại; cấu hình kết quả runtime vẫn NOT_RUN. |

Điều kiện FK và PL/pgSQL trên là kiểm tra tĩnh; không chứng minh migration, trigger, transaction isolation hoặc quyền service account đã chạy đúng. Chưa thực thi SQL, chưa seed database. Số thao tác không phải số tính năng đã triển khai.

### Cách tái lập

Dùng Python và [requirements-validation.txt](verification/requirements-validation.txt) trong môi trường công cụ riêng; đây không phải dependency của ứng dụng. Chạy từ thư mục design:

```powershell
python verification/verify-design-v0.1.py --output verification/results-v0.1.json
```

Các baseline bên cạnh design phải có đúng cấu trúc `docs/planning`, `docs/use-cases`, `docs/architecture`, `docs/requirements` và `docs/domain-model` như manifest. Dependency validation đã dùng: pglast 8.7, openapi-spec-validator 0.9.0, PyYAML 6.0.3, jsonschema 4.26.0. Cảnh báo deprecation của RefResolver không làm thất bại việc kiểm schema; phiên bản công cụ được pin để tái lập.

## 2. Render và đọc sơ đồ

PlantUML **1.2026.8**, Java **17.0.18**, headless, UTF-8, failfast2; SVG và PNG đều exit 0. JAR SHA-256: `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462`. [Script render](render-diagrams-v0.1.ps1) kiểm hash JAR trước khi chạy.

| Sơ đồ | Kích thước PNG | Kiểm tra |
| --- | --- | --- |
| [erd-context-access-v0.1](erd-context-access-v0.1.svg) | 1562 × 1334 | Render SVG/PNG thành công; đã mở PNG và đọc kiểm tra. |
| [erd-evidence-assessment-v0.1](erd-evidence-assessment-v0.1.svg) | 1251 × 1196 | Render SVG/PNG thành công; đã mở PNG và đọc kiểm tra. |
| [erd-risk-decisions-v0.1](erd-risk-decisions-v0.1.svg) | 2115 × 1747 | Render SVG/PNG thành công; đã mở PNG và đọc kiểm tra. |
| [upload-sequence-v0.1](upload-sequence-v0.1.svg) | 1161 × 1351 | Render SVG/PNG thành công; đã mở PNG và đọc kiểm tra. |

Đã kiểm tiêu đề, tên bảng/field, nhãn quan hệ, các trạng thái và khung chú giải; không bị cắt nội dung hoặc có trang lỗi PlantUML. Sơ đồ ERD chọn các quan hệ FK đơn chính; SQL là nguồn đầy đủ về khóa ghép, NULL và bảng con. Sơ đồ risk có nhiều nhãn nên dùng SVG để phóng to. Luồng upload thể hiện Browser → reverse proxy/TLS → policy gate → intake, staging/scan và kiểm lại trước commit; lỗi không trả thành công COMMITTED.

```powershell
./render-diagrams-v0.1.ps1 -PlantUmlJar <path-to-pinned-jar> -Java <path-to-java.exe>
```

## 3. Đối chiếu ngữ nghĩa và sửa sau review

Đã đọc đối chiếu [API](api-contract-v0.1.md), [data model](data-model-v0.1.md), [storage](storage-transactions-v0.1.md) và baseline; các sửa sau review nằm trong phiên bản này:

- Tạo context trước assessment/scenario để tránh vòng bootstrap; assessment_scenario lưu đủ nhiều scenario trong một assessment.
- Bổ sung persistence cho ScenarioSnapshot, InputConfirmation, ImpactConfirmation, EvidenceRequest và TreatmentApproval; exact snapshot/task version và citation có liên kết typed.
- Retest giữ nhiều baseline/output control, task và evidence; API ASSESSMENTS_RECORDED ánh xạ DB COMPLETED; input request và bảng con được khóa lịch sử.
- Adjudication lưu nhiều review decision và resolved_fields; closure giữ bằng chứng theo tiêu chí, retest control và phiên bản target trước/sau.
- Scope có scenario_ids; ControlImplementation gắn exact authentication profile; RiskControlLink có scope/provenance và bất biến; EvidenceLink có nhiều criterion.
- Comparison lưu exact task versions và attribution evidence. SUPPORTED cần review độc lập CONFIRMED, actor/time và task/evidence; treatment plan là nhóm tùy chọn.
- Plausibility dùng MEDIUM theo RM-01, khác risk level MODERATE. Priority approval action APPROVE/REJECT tách kết quả RANKED/NOT_RANKED.
- Payload canonical có schema version giữ cấu trúc DTO, raw claim/source metadata; service phải đồng bộ typed columns/FK/children và hash trong một transaction.
- Trigger ngăn sửa/xóa lịch sử, thêm child sau transaction tạo, sai snapshot kind hoặc thiếu payload; version mutable tăng đúng một; storage transition riêng. Runtime role phải không có quyền DDL/TRUNCATE/disable trigger; provisioning và transaction tests thuộc bước 06.

[Traceability](traceability-v0.1.md) ánh xạ NOTE-01…10, SC-01/SC-02, FLOW-01…10 và yêu cầu. Đây là review thiết kế của trợ lý, chưa phải xác nhận nghiệm thu của người dùng/SME.

## 4. Việc chưa kiểm chứng

- Migration DDL trên PostgreSQL 17, Django models/migrations, transaction services và adapter DTO chưa chạy.
- Quyền theo scope/assignment/expiry tại read, commit và stream; revoke race, idempotency race, OCC và dependency conflict chưa kiểm trên runtime.
- Scanner fail-closed, hash mismatch, file/DB crash windows, orphan reconciliation, lease/fencing, export expiry và restore chưa kiểm thực tế.
- RM service, đầy đủ criteria, độc lập reviewer/adjudicator, bất biến snapshot/as_of, attribution và closure cần kiểm service với dữ liệu thật/fixture phù hợp.
- Tài nguyên VM, thời gian scan/upload/report và capacity chưa đo. Các con số cấu hình là thiết kế.
- FLOW-01…10, TC-01 T01–T24, VALID-G-01 **NOT_RUN**; hai phiếu G trống; chưa có CRM evidence, lab hoặc SME calibration.
- Năm cấu hình AUTH-CRM-01 và môi trường/owner approval phải được chốt trước lab. MF-03/MF-04 **NOT_RANKED**, chưa được SME phê duyệt.

Hoàn tất thiết kế Bước 05 không thay thế các kiểm chứng này; Bước 06 không được khởi động trong lượt hoàn tất này.
