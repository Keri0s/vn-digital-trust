# Planning — tài liệu đang sử dụng

**Cập nhật:** 2026-10-23. **Bước 01:** COMPLETE về thiết kế. **Bước 02:** COMPLETE — DESIGN_FROZEN. **Bước 03:** COMPLETE về thiết kế v0.2-r1; sơ đồ đã render/đọc kiểm tra và được người dùng xác nhận ngày 2026-10-18 (kế hoạch mục 22–23). **Bước 04:** COMPLETE về thiết kế kiến trúc v0.1 (mục 25). **Bước 05:** COMPLETE về thiết kế v0.1 (mục 28). **Bước 06:** IN_PROGRESS — mục 29. VALID-G-01 ở bước 06: NOT_RUN; độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng.

**Bước 05 hoàn tất thiết kế ngày 2026-10-21: [bộ tài liệu](../design/README.md), [kiểm tra](../design/validation-v0.1.md). Bước 06 đã bắt đầu theo yêu cầu ngày 2026-10-23; kết quả tại [hồ sơ triển khai](../implementation/README.md).**

Đây là chỉ mục hiện hành. Các bản đã thay thế nằm trong `history/`; chúng phục vụ truy vết quyết định và không dùng cho assessment mới.

## 1. Nên đọc gì trước?

1. [Kế hoạch thực hiện](execution-plan-v0.1.md) — tiến độ 6 bước; kết quả bước 05 tại mục 28, lưu ý tại mục 27; bàn giao 04 → 05 và yêu cầu chờ lưu ý ở mục 26, kết quả kiến trúc ở mục 25; bàn giao bước 03 → 04 và phạm vi kiến trúc hiện hành ở mục 24; kết quả bước 03 đã đính chính ở mục 22, xác nhận sơ đồ của người dùng ở mục 23 và bàn giao bước 02 → 03 ở mục 20; biên bản đóng thiết kế/VALID-G-01 ở mục 19; tổ chức thư mục ở mục 18.
2. [Phương pháp risk RM-01](risk-method-v0.4.md) — **v0.4-r3**, calculation profile vẫn v0.4; công thức, UNKNOWN, impact_progress, giới hạn và quy tắc review.
3. [Control và evidence CE-01](control-evidence-v0.1.md) — tiêu chí, bằng chứng và cách kết luận control.
4. [Ca kiểm thử TC-01](control-test-cases-v0.1.md) — 24 ca thiết kế; chưa chạy CRM/lab.

Đầu ra bước 04: [kiến trúc kỹ thuật v0.1](../architecture/architecture-technical-v0.1.md) và [biên bản kiểm tra sơ đồ](../architecture/diagram-validation-v0.1.md); kết quả tại kế hoạch mục 25.

Đầu ra bước 03: [use case v0.2-r1](../use-cases/use-cases-technical-v0.2.md), [kiểm tra sơ đồ](../use-cases/diagram-validation-v0.2-r1.md) và [fixture quyền/luồng bổ sung](../use-cases/flow-fixtures-v0.2.json). Phần bổ sung không sửa fixture baseline.

Khi cần bối cảnh: [phạm vi lab](lab-scope-and-fixtures-v0.1.md) và [dữ liệu lab giả lập](lab-fixtures-v0.1.json). Khi muốn kiểm tra công thức: [hướng dẫn tái lập](verification/README.md) và [báo cáo review](verification/risk-method-review-v0.4.md).

## 2. Cấu trúc chuẩn

```text
planning/
  README.md
  execution-plan-v0.1.md
  lab-scope-and-fixtures-v0.1.md
  lab-fixtures-v0.1.json
  risk-method-v0.4.md
  control-evidence-v0.1.md
  control-test-cases-v0.1.md
  verification/              # hướng dẫn, báo cáo, dữ liệu và script kiểm tra
  review-forms/              # hai phiếu G v0.4 chưa điền
  history/                   # các bản đã thay thế, có chỉ mục riêng
```

### Giữ ở bộ hiện hành

| Nhóm | Tài liệu cần giữ | Vai trò |
| --- | --- | --- |
| Kế hoạch | execution-plan-v0.1.md | Một nơi theo dõi tiến độ và nhật ký quyết định |
| Phạm vi | lab-scope-and-fixtures-v0.1.md + lab-fixtures-v0.1.json | Context và dữ liệu giả lập đã chọn ở bước 01 |
| Phương pháp | risk-method-v0.4.md | Quy tắc RM-01 v0.4-r3 đã đóng băng thiết kế |
| Control | control-evidence-v0.1.md + control-test-cases-v0.1.md | Tiêu chí/evidence và expected results trước lab |
| Kiểm tra | 6 tệp trong verification/ | Tái lập số học và giải thích giới hạn; giữ script, hai JSON fixture, JSON kết quả cạnh nhau |
| Chấm G | [Phiếu A](review-forms/risk-g-rating-a-v0.4.md) và [phiếu B](review-forms/risk-g-rating-b-v0.4.md) | Hai người chấm độc lập; hiện vẫn trống, NOT_RUN |

**Version tính riêng cho từng tài liệu.** CE-01/TC-01 và hồ sơ lab v0.1 vẫn là bản hiện hành; không chuyển chúng vào history chỉ vì số version thấp hơn RM-01 v0.4. Bản phương pháp ghi r3 ở phần đầu; giữ tên file v0.4 vì calculation profile không đổi.

### Chỉ giữ trong lịch sử

- `history/risk-v0.1/`: phương pháp L×I ban đầu.
- `history/risk-v0.2/`: phương pháp nhiều yếu tố ban đầu và fixture tương ứng.
- `history/risk-v0.3/`: phương pháp, fixture, báo cáo và phiếu G đã được v0.4 thay thế.
- `history/risk-v0.4-before-r2/`: snapshot phương pháp, báo cáo, kế hoạch và README trước đính chính r2.
- `history/risk-v0.4-r2.zip`: một gói giữ bản trước r3 và đầy đủ bộ kiểm tra theo hash cũ, để tái lập khi cần.

Xem [chỉ mục lịch sử](history/README.md). Những bản này được giữ để giải thích quá trình thay đổi; không phải các lựa chọn phương pháp ngang hàng với bản hiện hành. Chưa có tệp nào cần xóa hẳn trong lần chuẩn hóa này.

## 3. Tóm tắt những gì đã thay đổi

| Mốc | Thay đổi chính |
| --- | --- |
| RM-01 v0.1 | Bắt đầu bằng L×I; làm rõ điểm truy cập của IBM khác chỉ số rủi ro scenario của SME. |
| v0.2 | Chuyển sang E/F/G và CIA + hậu quả nghiệp vụ; trọng số E/F 40/60, G điều chỉnh khả thi, impact lấy max; đánh giá có điều kiện theo scenario. |
| v0.3 | Thêm cổng impact, khoảng cận cho UNKNOWN, rubric G theo từng đường, độ nhạy từng yếu tố và phiếu A/B. Chuẩn hóa Integrity thành I_integrity, impact tổng thành I_total. |
| v0.4 | Thống nhất max G/impact; hai cận R25 bằng nhau thì có điểm và nhãn dù vẫn cần review; tính bằng R25 nguyên; hiển thị cắt xuống một chữ số thập phân. G=1 ⇒ R≤9 là hệ quả được ghi rõ. |
| v0.4-r2 | Thêm impact_progress để ghi nhận tiến bộ từng chiều khi R chưa đổi; khôi phục quy tắc so CURRENT/INHERENT, không cộng scenario/tactic, confidence không nhân R, bất đồng giữ review. Tách kết luận từng ca khỏi phương pháp; bổ sung bảng trọng số hai ca, sửa dẫn NIST và công bố bộ kiểm tra độc lập. |
| v0.4-r3 — hiện hành | Khôi phục quy tắc AI/fixture; xác nhận số trang NIST r2 đúng; sửa chỉ mục/chat/trạng thái lab criteria; thêm verified_worsening và summary max/số chiều; ghi rõ thẩm quyền quyết định cặp. Đóng thiết kế bước 02, chuyển kiểm chứng G sang VALID-G-01 bước 06 (NOT_RUN). |
| Chuẩn hóa thư mục | Cấp ngoài giảm từ 22 tệp xuống 7 tệp, gồm README mới và 6 tệp chính. Chuyển 16 tệp vào nhóm phù hợp; giữ đủ dữ liệu/lịch sử, cập nhật liên kết. |

**Kết luận hiện hành cho MF-03/MF-04:** cả hai HIGH; `priority_decision=NOT_RANKED`, `decision_type=REVIEWER_DETERMINATION` của trợ lý với dữ liệu đang có; người dùng chưa xác nhận/đổi (NOT_RECORDED). Dòng xác nhận và lý do nằm ở báo cáo review mục 4. Nhận xét trước đây đề xuất MF-04 trước đã được thay thế, chỉ còn là lịch sử trong báo cáo/kế hoạch.

## 4. Đã kiểm tra và còn thiếu

- Số học đã được đối chiếu bằng script độc lập: 26 ca chính, 625 tổ hợp, 50.625 hộp miền, 182 hàng độ nhạy; thêm 20 ca impact_progress. Đây là kiểm tra mô hình, chưa là hiệu chuẩn SME hoặc evidence CRM.
- Hai phiếu G còn NOT_RUN, thuộc VALID-G-01 ở bước 06. Độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng; đây là giới hạn kiểm chứng được ghi rõ khi đóng băng thiết kế bước 02.
- Chưa có lab/evidence thực tế, chưa chạy 24 ca CRM, Atomic hoặc Caldera. Các giá trị TTL, chính sách phiên và môi trường vẫn phải chốt trước lab.
- Bước 02 đóng băng về thiết kế theo phạm vi/điều kiện tại kế hoạch mục 19. Người dùng đã yêu cầu bàn giao sang bước 03 ngày 2026-10-13; chat bước 03 đã đính chính và kiểm tra thiết kế luồng v0.2-r1 theo mục 22. Hai SVG cũ không đạt gate UML; bản mới được render trực tiếp và đọc ảnh. Người dùng yêu cầu đóng gói/bàn giao ngày 2026-10-18: bước 04 COMPLETE về thiết kế theo mục 25; bước 05 đang thực hiện thiết kế theo mục 27; bước 06 chưa bắt đầu.

## 5. Quy tắc duy trì thư mục

1. Mỗi tài liệu chỉ có một bản hiện hành trong nhóm của nó. Tạo bản thay thế thì chuyển bản cũ cùng các fixture/phụ lục liên quan vào history và cập nhật chỉ mục.
2. Phân biệt đổi calculation profile với chỉnh câu chữ/đường dẫn. Thay hệ số/quy tắc tính phải có version; tổ chức thư mục không tạo phương pháp mới.
3. Không chép thêm nhiều bản backup vào cấp ngoài. Snapshot cần giữ phải có mục đích rõ trong chỉ mục history; không tự tạo bản sao sau mọi lần chỉnh.
4. Giữ script và hai fixture JSON cạnh nhau trong verification để bộ kiểm tra chạy độc lập; cập nhật kết quả/hash khi dữ liệu hoặc script thay đổi.
5. Tài liệu history chỉ được sửa liên kết khi đổi vị trí; không sửa kết luận cũ thành kết luận hiện hành. Truy vết thay đổi trong execution-plan.

