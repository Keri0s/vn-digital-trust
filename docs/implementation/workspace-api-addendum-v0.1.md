# Bổ sung API runtime cho chuẩn bị hồ sơ v0.1

Ngày 2026-10-27. Tài liệu này mô tả phần đã triển khai tại Step06; không sửa bộ thiết kế/OpenAPI đã đóng băng ở Step05. Validator workspace sao chép bộ schema nền và chỉ bổ sung các thành phần dưới đây. Các endpoint quản trị vẫn dùng validator cũ.

## Endpoint

| Đường dẫn sau `/api/v1` | Phương thức | Hành vi |
| --- | --- | --- |
| `/systems`, `/assets`, `/data-assets` | GET, POST | Danh sách có phân trang/phạm vi; tạo inventory |
| `/systems/{id}`, `/assets/{id}`, `/data-assets/{id}` | GET, PATCH | Đọc/cập nhật hồ sơ, trả ETag |
| `/context-snapshots` | POST | Chụp inventory đã chọn và bối cảnh bất biến |
| `/context-snapshots/{id}` | GET | Đọc bối cảnh theo quyền hiện hành |
| `/scenarios`, `/scenarios/{id}` | GET; POST collection; PATCH item | Kịch bản mới ở DRAFT; thay đổi tạo snapshot mới |
| `/scenarios/{id}/transitions` | POST | DRAFT/ACTIVE → ACTIVE/RETIRED hợp lệ, từ chối trạng thái trùng và sửa RETIRED |
| `/scenario-snapshots/{id}` | GET | Đọc snapshot theo quyền hiện hành |
| `/assessments/{id}/scenario-links` | POST | Gắn kịch bản ACTIVE vào đợt OPEN, giữ snapshot cụ thể |
| `/assessments/{id}/dossier` | GET | Hồ sơ đã được cấp quyền, gồm snapshot và inventory đã chụp |
| `/workspace/setup` | GET | Tổ chức, chi nhánh có đủ quyền, người phụ trách hợp lệ và version cần cho form |

Ghi yêu cầu phiên hợp lệ, mật khẩu tạm đã đổi, CSRF và `Idempotency-Key`. PATCH và hai lệnh transitions/scenario-links yêu cầu `If-Match: "<version>"` của đối tượng cập nhật. `write_context` gồm lý do và phiên bản phụ thuộc. Dữ liệu JSON đóng, UUID, kiểu và trường dư được kiểm ở boundary. Body ghi dùng DTO Step05 tương ứng; unsupported vendor/data-flow/evidence source trả lỗi rõ ràng.

## Dependency version

Enum `Dependency.resource_type` của validator workspace bổ sung `branch`, `system`, `asset`, `data_asset` để kiểm phiên bản đọc lúc soạn lệnh. Ngoài tổ chức, server yêu cầu chi nhánh, người phụ trách nếu có, đối tượng liên quan và/hoặc inventory được chọn đúng loại lệnh. Kịch bản dùng version inventory hiện hành để kiểm khả dụng, nhưng bản chụp bối cảnh cũ vẫn giữ nguyên nội dung. Dependency thiếu hoặc lỗi phiên bản bị từ chối. Không thay thế kiểm quyền bằng dependency version.

## Lệnh gắn kịch bản

`AssessmentScenarioLinkInput` gồm đúng `scenario_id` và `write_context`. Dependency bắt buộc: tổ chức và kịch bản; If-Match là phiên bản của đợt. Server kiểm `assessment.run` trên đợt và kịch bản, cùng tổ chức/phạm vi, trạng thái OPEN/ACTIVE, chưa gắn và không vượt 200 kịch bản/đợt. Lưu `assessment_scenario.scenario_snapshot_id`, tăng phiên bản đợt, đồng bộ DTO và history/audit. Response 200 là DTO Assessment mới với ETag mới. Không có lệnh tháo, thay thế hoặc tự cập nhật bản đã gắn ở mốc này.

## Hồ sơ và selector

`GET dossier` trả `{assessment, items, restricted}`. Mỗi item là `{scenario, context, inventory, owner_name, state}`; `scenario`/`context` là DTO snapshot, `inventory` chứa các nhóm `systems`, `assets`, `data-assets` được chụp, tên người phụ trách và trạng thái là dữ kiện đã lưu. Server xác minh membership và snapshot, lọc từng item theo scope hiện hành. `restricted=true` nếu có item bị lọc; không cung cấp dữ liệu bị chặn. Reviewer gắn với assessment phải đi qua dossier; không được truy cập danh mục toàn cục hoặc dùng ID để mở rộng quyền. Endpoint ghi audit đọc hồ sơ.

`GET setup` yêu cầu `inventory.manage` và `risk.propose`, chỉ trả chi nhánh đang hoạt động có đủ cả hai quyền. Người phụ trách là người đang hoạt động trong tổ chức, có liên kết chi nhánh hoặc là chính người thao tác. Giao diện hiện dành cho Security theo chi nhánh; ADMIN không tự có quyền nghiệp vụ.

## Snapshot và migration

Snapshot runtime có `api_payload_schema_version=workspace-v0.1`. Hash SHA-256 được tính trên JSON canonical `{payload, facts}`, trong đó `payload` loại hai trường `created_at` và `content_sha256`; `facts` giữ inventory/owner/state tương ứng. Mốc thời gian không tham gia hash này vì do trigger server quyết định. Trigger metadata đồng bộ `api_payload.created_at` với `snapshot_registry.created_at`; đọc snapshot vẫn kiểm cả timestamp, tác giả, scope, schema và hash. Các trigger bất biến của nền tảng vẫn giữ nguyên.

Migration `0004_workspace_runtime` thêm FK nullable `assessment_scenario.scenario_snapshot_id` và trigger metadata. Không sửa hàng cũ, thêm bảng hoặc thêm quyền DELETE. Trước khi triển khai phải sao lưu và kiểm không có liên kết cũ chưa xác định snapshot. Reverse migration chỉ chạy khi chưa có workspace snapshot hoặc binding; nếu đã có dữ liệu mới, nó từ chối để tránh mất lịch sử. Khi đó phục hồi phải dùng quy trình backup/restore được duyệt, không cưỡng ép downgrade.

## Giới hạn

Một chi nhánh/hồ sơ; liên kết inventory chỉ bổ sung; scope không chuyển tại chỗ. Chưa có upload/stream bằng chứng, scan, verification decision, control/risk evaluation, independent review decision hoặc CRM flows. ACTIVE của kịch bản không đồng nghĩa VERIFIED của bằng chứng. Không thay đổi các trục `storage_state`, `verification_mode`, `assessment_mode`, `review_outcome` trong thiết kế nền.
