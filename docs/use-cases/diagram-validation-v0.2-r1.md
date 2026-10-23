# Kiểm tra sơ đồ và đính chính luồng — v0.2-r1

**Ngày:** 2026-10-17 (Asia/Bangkok). **Người thực hiện:** trợ lý Codex. **Phạm vi:** kiểm tra thiết kế và render; không là test CRM/lab hoặc phê duyệt risk SME.

## 1. Lỗi và kết quả sửa

Hai SVG ngày 2026-10-13 là hình tuyến tính được viết riêng, không được render từ nguồn PlantUML. Vì vậy sequence không có lifeline/alt/opt và activity mất rẽ nhánh. Kiểm tra XML/nhãn khi đó không đủ để xác nhận UML đúng; kết luận đạt gate sơ đồ ở kế hoạch mục 21 được đính chính bởi mục 22. Bản trước sửa được giữ trong [gói lịch sử](../planning/history/step03-v0.2-before-r1.zip).

| Đầu ra | Đối chiếu đã thực hiện | Kết quả |
| --- | --- | --- |
| [Sequence SVG](retest-sequence-v0.2.svg) / [PNG](retest-sequence-v0.2.png) | Render trực tiếp [nguồn](retest-sequence-v0.2.puml); năm đường đời dọc: IT/Security, Risk Owner, Reviewer, VN Digital Trust, Assessment history; message ngang; 7 alt và 3 opt | Đã đọc ảnh PNG, khung/nhãn/nhánh không bị cắt; xác nhận 5 đường dọc nét đứt và các nhãn alt/opt trong SVG |
| [Activity SVG](assessment-flow-v0.2.svg) / [PNG](assessment-flow-v0.2.png) | Render trực tiếp [nguồn](assessment-flow-v0.2.puml); 8 nút điều kiện với nhánh và điểm hợp luồng | Đã đọc ảnh PNG từ đầu đến cuối; các nhánh quyền, context, failure/satisfaction, input, yêu cầu retest, evidence retest và điều kiện đóng đều hiện rõ |
| Quyền/context | Tách từ chối do thiếu/hết hạn quyền khỏi validation lỗi context | Quyền bị từ chối không đọc/sửa nghiệp vụ; context thiếu được ghi NEEDS_REVIEW với score/range/level null |
| Trật tự G | TUC-05/06 tạo ControlAssessment trước khi TUC-04 xác nhận G | CURRENT có coverage và strength theo đường; phần chưa xác minh giữ UNKNOWN; không ánh xạ result trực tiếp thành G |
| Xác minh nội bộ | Nhánh IT/Security SELF_ASSESSED và nhánh Reviewer tùy chọn; quyền bổ sung có scope | Consultant hết hạn không chặn người nội bộ còn quyền; lời khai không tự trở thành evidence VERIFIED |
| Status và ưu tiên | Status giữ EVALUATED/NEEDS_REVIEW; mode/outcome review riêng. Risk Owner chốt ưu tiên vận hành | Không đồng nhất reviewer determination với phê duyệt SME; MF-03/MF-04 vẫn NOT_RANKED |
| Kết quả trộn và retest | Failure đã xác minh được giữ dù tiêu chí khác INCONCLUSIVE/thiếu evidence; evidence VERIFIED chưa đủ đóng gap | CONTROL_GAP và EVIDENCE_GAP có thể cùng tồn tại; closure có tiêu chí/quyền/quyết định riêng |

## 2. Tái tạo bản render

Renderer: **PlantUML 1.2026.8**, commit `149874a`, chạy với Java 17.0.18. JAR tải từ [trang chính thức](https://plantuml.com/download) qua [release 1.2026.8](https://github.com/plantuml/plantuml/releases/tag/v1.2026.8). SHA-256 JAR đã dùng: `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462`.

Chạy từ PowerShell với JAR đã tải; Java/JAR không được đóng gói trong tài liệu dự án:

```powershell
./render-diagrams-v0.2.ps1 -PlantUmlJar 'path/to/plantuml-1.2026.8.jar' -Java 'path/to/java.exe'
```

[Script](render-diagrams-v0.2.ps1) kiểm tra hash JAR và gọi renderer với UTF-8, headless, `-failfast2`, lần lượt SVG/PNG. Cả hai lần render trả exit code 0; SVG không chứa lỗi cú pháp hoặc cảnh báo render. PNG phục vụ đọc hình; SVG phục vụ phóng to. Bộ tạo hộp tuyến tính cũ trong thư mục làm việc đã được thay bằng lời gọi renderer.

## 3. Walkthrough bổ sung và giới hạn kiểm tra

[FLOW-03-v0.2-r1](flow-fixtures-v0.2.json) là phần bổ sung quyền/ca thiết kế dựa trên hash của `lab-fixtures-v0.1.json`, không ghi đè baseline. Đã đọc đối chiếu mười ca với các nhánh:

| Ca | Nhánh/đối chiếu thiết kế |
| --- | --- |
| FLOW-01/02/03 | Self-assessment không cần consultant; reviewer đúng/sai scope; từ chối đúng mốc hết hạn với đồng hồ fixture rõ ràng |
| FLOW-04 | Risk Owner chốt ưu tiên; consultant chỉ đề xuất |
| FLOW-05/06 | Thiếu evidence/test T23 không kết luận failure; failure đã xác minh cùng phần UNKNOWN giữ hai loại gap |
| FLOW-07 | SC-02 có phiên đọc; thiếu đường/đích chính sách không dùng MFA login mới để hạ G |
| FLOW-08/09 | Retest tạo revision/snapshot; fail/INCONCLUSIVE không tự đóng; closure đạt tiêu chí có quyết định; so không tương đương là NOT_COMPARABLE |
| FLOW-10 | Context/miền lỗi không có score hoặc range |

Đã xác nhận hash baseline và ID role trong overlay, đọc đối chiếu nguồn với một lượt review riêng. Đây là **DESIGN_WALKTHROUGH**, trạng thái thực thi ca vẫn **NOT_RUN**. Không có backend/RBAC/test lab được chạy trong lần sửa này. RM-01, CE-01, TC-01, bộ verification của bước 02 và fixture baseline được giữ nguyên.

## 4. Hash đầu ra

| Tệp | SHA-256 |
| --- | --- |
| `assessment-flow-v0.2.puml` | `605c4ae4bf8db23314ad0d1607da97e23744c698aad9adbd4923460e66753190` |
| `assessment-flow-v0.2.svg` | `efe03b80fd89bba366e4a03fda6ceffb4c179c51371d8055e34e9257c15da574` |
| `assessment-flow-v0.2.png` | `20a2785844f5fac250878ed6f2e3c0dd0347b5727dc04974c9d659f6dcc12336` |
| `retest-sequence-v0.2.puml` | `9a7d429c75d40f1892a740ccfa451e14f4fd42dcc0b6c61978ad17b778a52590` |
| `retest-sequence-v0.2.svg` | `74b84ab4e804811759a8e4dd1c45ed247830f10667849c9b7b641e1bebcc3f44` |
| `retest-sequence-v0.2.png` | `9c0327d77248219d662674981a96f3bc8c8442ade867489e1053b11365958202` |
| `use-cases-technical-v0.2.md` | `7a7c7de6c764548c7c5fa35c855d98a8484afd9191f463faa7b4bc93a5feced7` |
| `flow-fixtures-v0.2.json` | `820fe1a8722c07ea81a61e4865c9f89457e78f95fbc1ff845528cf6b4708497a` |
| `render-diagrams-v0.2.ps1` | `1afd018dfb7567f62a4703af1c18f10c976b7a4107b6f9666191d4a88c3a804a` |
