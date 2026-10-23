# RM-01 v0.3 — Chỉ số risk có điều kiện và review evidence

**Ngày:** 2026-10-10. **Trạng thái:** DRAFT_REVIEW; bước 02 IN_PROGRESS. Bản này thay v0.2 cho công việc review hiện tại; giữ nguyên các bản cũ. Chưa có kết quả lab, hiệu chuẩn SME hoặc kết quả hai người chấm độc lập.

Tài liệu liên quan: [control/evidence](../../control-evidence-v0.1.md), [ca kiểm thử control](../../control-test-cases-v0.1.md), [kế hoạch](../../execution-plan-v0.1.md), [fixture và kỳ vọng](risk-method-fixtures-v0.3.json), [phân tích độ nhạy/kiểm tra](risk-method-review-v0.3.md), [phiếu chấm độc lập A](risk-g-rating-a-v0.3.md), [phiếu chấm độc lập B](risk-g-rating-b-v0.3.md).

## 1. Mục đích và cách dùng register

R chủ yếu dùng để đối chiếu **trước/sau treatment của cùng scenario, tiền điều kiện và phạm vi hậu quả**, cùng method/profile. Nếu môi trường, năng lực đối thủ, scope hoặc cách đặt tiền điều kiện thay đổi, phải ghi rõ; không quy toàn bộ chênh lệch R cho treatment. Lưu các yếu tố thay đổi và evidence tương ứng. Giảm điểm không đồng nghĩa đo được tỷ lệ giảm tổn thất.

Profile `CONDITIONAL-BASE-v0.3` giả định tiền điều kiện đã đúng. Với SC-01 đã tới CRM qua VPN và biết mật khẩu; SC-02 đã có phiên đọc, E thường là 5. Khi E=5, P=2+0.6F; việc E không phân biệt hai case là giới hạn được thừa nhận. E chỉ mô tả cơ hội hành động còn lại trong trạng thái đã giả định, không đại diện tần suất năm. Không tự hạ E để làm đẹp điểm.

Register vẫn chứa SC-01 và SC-02, kể cả NEEDS_REVIEW. Mặc định nhóm theo scenario và lịch sử treatment; không tự xếp toàn bộ scenario theo R. Khi reviewer muốn so sánh chéo, phải hiển thị cạnh nhau: tiền điều kiện, `precondition_plausibility`, kỳ xem xét, C/I_integrity/A/B, evidence gaps, control failures và R/range. Kết quả ưu tiên là quyết định reviewer có lý do; không suy thứ tự từ R đơn lẻ hoặc nhân nhãn độ khả dĩ vào R. Với score_range, không dùng cận trên, cận dưới hay trung điểm để xếp hạng.

`precondition_plausibility` đánh giá khả năng các tiền điều kiện đồng thời tồn tại **ngoài giả định lab**, theo một kỳ xem xét chung (đề xuất 12 tháng nếu SME xác nhận):

| Nhãn | Căn cứ cần có |
| --- | --- |
| LOW | Có trở ngại cụ thể khiến tập tiền điều kiện khó đồng thời đạt; không chỉ dựa vào chưa thấy sự cố |
| MEDIUM | Có đường khả thi để đạt tập điều kiện, nhưng chưa đủ căn cứ cho LOW/HIGH |
| HIGH | Có evidence gần bối cảnh về điều kiện thường xuyên sẵn có hoặc đã nhiều lần xảy ra |
| UNKNOWN | Chưa có căn cứ, chưa chọn kỳ xem xét hoặc các nhận định mâu thuẫn |

Mỗi nhãn có reason/source, reviewer và as_of/horizon; đây là nhận định riêng, không phải xác suất đã hiệu chuẩn. Chỉ giả định biết mật khẩu trong SC-01 không đủ để gán HIGH cho khả năng mật khẩu thực tế bị lộ. Nếu nhãn UNKNOWN, so sánh chéo chỉ là review tạm, không là xếp hạng tự động đã xác nhận.

## 2. Phép tính giữ lại và cổng impact mới

Các điểm đầu vào nguyên 1–5 là thứ bậc. Công thức do dự án đề xuất, chưa được chứng minh có khoảng cách đều giữa các mức:

```text
P = 0.40 × E + 0.60 × F
L = 1 + (P − 1) × G / 5
I_total = max(C, I_integrity, A, B)
R = L × I_total

raw_level(R): [1,5) LOW; [5,10) MODERATE; [10,17) HIGH; [17,25] CRITICAL
final_level(R,I_total):
  I_total = 1  → LOW
  I_total = 2  → min(raw_level(R), MODERATE)
  I_total ≥ 3  → raw_level(R)
```

Thứ tự nhãn: LOW < MODERATE < HIGH < CRITICAL. R giữ nguyên, lưu `raw_level`, `risk_level` và `impact_gate_reason` để giải thích. Ví dụ L=5/I_total=1: R=5, raw MODERATE nhưng final LOW; L=5/I_total=2: R=10, raw HIGH nhưng final MODERATE. Đây là quy tắc ưu tiên dựa vào impact do dự án thiết kế, không thay kết luận control hoặc tự động chấp nhận risk.

40/60 và G/5 tiếp tục là tham số thử nghiệm; G/5 không phải hiệu lực control được đo theo phần trăm. P/L/R dùng số đầy đủ để tính/phân mức. Giao diện đọc mặc định hiển thị R dạng **xấp xỉ số nguyên**, kèm nhãn và vector; chi tiết tính/fixture giữ số đầy đủ để tái lập, không gắn ý nghĩa đo lường cho hai số thập phân. Ví dụ R=9.72 hiển thị “≈10 · MODERATE”, kèm giải thích nhãn dựa trên giá trị trước làm tròn. Range hiển thị cận dưới làm tròn xuống và cận trên làm tròn lên, không làm hẹp range do làm tròn.

## 3. Ranh giới E/F/G và template scenario

| Mức | E — cơ hội còn lại sau tiền điều kiện | F — dễ thực hiện nếu bỏ đúng các control liệt kê để chấm G |
| --- | --- | --- |
| 1 | Nhiều cơ hội hiếm chưa sẵn | Cần năng lực/nguồn lực vượt xa đối thủ giả định |
| 2 | Cơ hội hạn chế, cần sắp xếp đáng kể | Kỹ năng cao, nhiều điều kiện kỹ thuật độc lập |
| 3 | Có cơ hội nhưng còn điều kiện bổ sung rõ | Kỹ năng trung bình, công cụ và chuẩn bị đáng kể |
| 4 | Cơ hội thường có, ít điều kiện bổ sung | Phương pháp sẵn, cần tùy chỉnh nhỏ |
| 5 | Có thể bắt đầu ngay | Hành động thường lệ, ít kỹ năng |

**Quy tắc F:** trước khi chấm, ghi `excluded_controls_for_F` gồm các control đang được đánh giá tại G. Chỉ giả định bỏ tác dụng của danh sách đó, giữ nguyên asset, scope, quyền ban đầu, năng lực đối thủ và các khó khăn khác. Không mô tả việc vượt WebAuthn trong rationale F rồi tiếp tục tính cùng tác dụng trong G. Nếu không mô tả được phản thực tế này một cách rõ ràng, F=UNKNOWN và cần review scope, không tự tách điểm tùy ý.

**Mẫu SC-01:** tiền điều kiện đã qua VPN, biết mật khẩu U102, không có phiên/WebAuthn; excluded_controls_for_F=[AC-DEMO-01]. E=5 và F=5 là giá trị template có lý do: vào trang và nhập mật khẩu là hành động thường lệ nếu tạm bỏ yêu cầu MFA. Việc chữ ký/origin/UV/enrollment/recovery có ngăn truy cập hay không nằm ở G. F có thể không đổi sau treatment; điều đó được kỳ vọng. Không dùng kết quả VPN để giảm G vì VPN đã được giả định đi qua.

**Mẫu SC-02:** E có thể điền sẵn 5 nếu tiền điều kiện giữ phiên đọc hợp lệ. F chưa điền sẵn 3 cho assessment thật vì đường chuyển chưa chọn; F=3 trong MF-03 chỉ là giả định để tính minh họa. Control xuất/đích truyền thuộc G, không dùng MFA cho phiên đã hợp lệ làm căn cứ hạ G.

### Giảm công việc nhập của SME

Template có ID/version, rationale/source dùng lại, trường nào là giả định và trạng thái `PROPOSED/CONFIRMED`. E/F được gợi ý từ template, người dùng xác nhận tiền điều kiện còn đúng; không bắt nhập lại bảy đoạn văn. Người dùng trả lời thay đổi thực tế và chọn hậu quả C/I_integrity/A/B từ mô tả; owner xác nhận impact. Có thể dùng cùng reference cho nhiều yếu tố với giải thích tác dụng khác nhau, không tính một tác dụng bảo vệ hai lần. Template tự điền không phải evidence được VERIFIED.

G có thể được gợi ý từ ControlAssessment bằng bảng ở mục 4, reviewer xác nhận. AI sau này có thể hỗ trợ trích thông tin/gợi ý có nguồn; quyền xác nhận, quy tắc và snapshot vẫn được giữ. Đây là yêu cầu phương pháp, chưa thiết kế API/UI/DB hoặc triển khai AI.

## 4. Chấm G: tách độ bao phủ và sức cản từng đường

Trước khi có G, liệt kê **các đường trọng yếu có thể dẫn tới sự kiện/hậu quả đã chọn**. Với AC-DEMO-01, template tối thiểu gồm login thông thường, đường tương tác thay thế trong scope, enrollment/thêm credential, recovery/thay yếu tố; credential/challenge/origin/UV/revocation là tiêu chí xuyên các đường liên quan. Tách login mới với phiên đã tồn tại; phiên bị đánh cắp không tự đưa vào SC-01.

Mỗi đường ghi: `path_id`, tiêu chí/control, `coverage=VERIFIED_COVERED/VERIFIED_UNCOVERED/UNKNOWN`, evidence revision, sức cản còn lại, mức g và rationale. Đường được chứng minh không áp dụng có reason được reviewer xác nhận; không bỏ đường vì chưa kiểm được. Coverage không có trọng số phần trăm: một bypass quan trọng không được trung bình hóa với nhiều đường đạt.

| g của đường | Quy tắc sức cản còn lại cần căn cứ |
| --- | --- |
| 1 | Tiêu chí trọng yếu trên đường đều được xác minh đạt; không phát hiện bypass trong scope kiểm tra |
| 2 | Có hạn chế phụ đã xác định, nhưng các cổng bắt buộc trên đường vẫn được xác minh đạt; ghi rõ vì sao hạn chế chưa tạo đường gây hậu quả |
| 3 | Có tiêu chí/biện pháp suy yếu được xác minh; còn một cản trở độc lập đáng kể **chưa có trong tiền điều kiện**, được chứng minh có hiệu lực; ghi cụ thể điều kiện bổ sung cần vượt |
| 4 | Control suy yếu, chỉ còn cản trở nhỏ theo năng lực đối thủ; evidence cho thấy chỉ cần điều chỉnh thông thường, không cần điều kiện độc lập đáng kể như g=3 |
| 5 | Đường được xác minh không có bảo vệ liên quan hoặc có thể đạt sự kiện/hậu quả dù control bắt buộc phải ngăn |

Nếu không phân biệt được cản trở đáng kể/nhỏ bằng evidence, giữ `g=UNKNOWN` hoặc ghi bất đồng chờ xử lý; không ép chọn 3 hay 4. VERIFIED_UNCOVERED → g=5. UNKNOWN coverage/strength → miền g=[1,5] cho tính cận. COVERED chỉ nói đã xét coverage, không tự tương đương g=1.

`G=max(g_path)` cho các đường áp dụng. Đủ evidence mọi đường mới xác nhận một G hoàn chỉnh. Nếu có đường chưa rõ, lưu `G_range=[max(các g đã biết,1),5]`, giữ G=UNKNOWN; kể cả cận dưới đã bằng 5, ghi coverage chưa đủ. Một bypass đã xác minh vẫn tạo CONTROL_GAP; không trì hoãn xử lý chỉ vì còn đường chưa biết.

| ControlAssessment và scope | Gợi ý cho reviewer, không tự quyết định G |
| --- | --- |
| SATISFIED | Gợi ý g=1 trên các đường/tiêu chí **thực sự được evidence bao phủ**; kiểm tra phần còn lại |
| PARTIALLY_SATISFIED | Xem từng đường và cản trở còn lại; không chuyển cố định sang g=3 |
| NOT_SATISFIED | Nếu đã chứng minh vượt bảo vệ dẫn tới sự kiện/hậu quả → g=5; nếu chỉ một lớp hỏng nhưng còn lớp độc lập hữu hiệu → reviewer xét g=3/4 có căn cứ |
| INSUFFICIENT_EVIDENCE / NOT_ASSESSED | UNKNOWN trên phần scope thiếu; cung cấp range, không suy control yếu hoặc mạnh |

Ví dụ: nếu mục tiêu control là không cấp phiên nghiệp vụ khi chỉ có mật khẩu, cấp được phiên này là vi phạm dù quyền dữ liệu sau đó hạn chế. Không dùng control quyền truy cập để sửa AC-DEMO-01 thành đạt. Control phát hiện sau khi dữ liệu đã ra ngoài không được ghi như ngăn được sự kiện. Thay đổi impact nhờ ứng cứu cần evidence riêng và không tính lại cùng tác dụng tại G.

## 5. Impact đối với CIA và nghiệp vụ; giới hạn của max

CIA triad gồm **Confidentiality (C) — tính bí mật, Integrity (I) — tính toàn vẹn, Availability (A) — tính sẵn sàng**. Trong các công thức, dùng `I_integrity` cho điểm hậu quả liên quan đến Integrity và `I_total` cho Impact tổng hợp để tránh trùng ký hiệu.

**Integrity — tính toàn vẹn** đề cập đến tính chính xác và đầy đủ của thông tin. Điểm `I_integrity` trong mô hình này thể hiện mức độ hậu quả khi tính toàn vẹn bị xâm phạm, chẳng hạn dữ liệu bị sửa đổi hoặc xóa trái phép, hoặc sai sót làm dữ liệu không còn chính xác hay đầy đủ. Đây là thành phần I của CIA triad; điểm số đánh giá hậu quả, không định nghĩa thêm một tính chất bảo mật hay đo mức mạnh của control. Tham chiếu thuật ngữ: [NIST — Security](https://csrc.nist.gov/glossary/term/security) và [NIST — Integrity](https://csrc.nist.gov/glossary/term/integrity).

**B** là chiều hậu quả nghiệp vụ/phục hồi bổ sung của mô hình, không thuộc CIA triad. C, I_integrity và A chấm hậu quả đối với ba thuộc tính CIA; B ghi ảnh hưởng nghiệp vụ tương ứng. Giữ các điểm ở thang 1–5 và owner xác nhận. Dữ liệu lab giả lập không tự chứng minh hậu quả doanh nghiệp nhỏ.

| Mức | C — hậu quả mất Confidentiality | I_integrity — hậu quả mất Integrity | A — hậu quả mất Availability | B — hậu quả nghiệp vụ/phục hồi |
| --- | --- | --- | --- | --- |
| 1 | Không lộ thông tin nhạy cảm | Không có tổn hại đáng kể đến tính chính xác/đầy đủ của dữ liệu | Không gián đoạn đáng kể | Xử lý thường lệ, không tổn thất đáng kể |
| 2 | Tập nhỏ, nhạy cảm thấp | Một số ít bản ghi sai lệch/thiếu, đối chiếu và khôi phục đơn giản | Cục bộ, ảnh hưởng nhẹ | Khắc phục trong công việc thường ngày |
| 3 | Dữ liệu nhạy cảm phạm vi giới hạn | Dữ liệu sai lệch/thiếu ảnh hưởng một quy trình hoặc chi nhánh | Quy trình quan trọng có gián đoạn, có cách làm tạm | Điều tra/khôi phục có kế hoạch |
| 4 | Dữ liệu nhạy cảm đáng kể/nhiều nhóm | Tính chính xác/đầy đủ của dữ liệu trọng yếu bị xâm phạm, ảnh hưởng quyết định của nhiều nhóm | Nhiều chi nhánh hoặc quy trình chính ngừng đáng kể | Nguồn lực lớn, ảnh hưởng khách hàng/đối tác đáng kể |
| 5 | Dữ liệu cốt lõi/đặc biệt nhạy cảm, hậu quả nghiêm trọng | Không còn tin cậy tính chính xác/đầy đủ của dữ liệu cốt lõi; hậu quả khó đảo ngược | Hoạt động cốt lõi ngừng kéo dài, phục hồi bị đe dọa | Đe dọa khả năng tiếp tục hoạt động hoặc tổn thất nghiêm trọng |

Mức thời gian/chi phí/phạm vi cụ thể vẫn cần bối cảnh và owner; không coi bảng định tính là hiệu chuẩn SME. Chưa rõ nhận UNKNOWN; không bị ảnh hưởng nhận 1 có lý do.

Max không biểu diễn độ rộng hậu quả. Bắt buộc giữ vector, các chiều bằng mức lớn nhất và mô tả phạm vi. MF-03 có (4,1,1,3), R=12.96; MF-04 có (4,4,3,4), R=12.32. Cả hai HIGH. Việc MF-04 có hậu quả rộng hơn chưa làm R cao hơn vì P khác nhau và max chỉ giữ I_total=4. Không tự kết luận MF-03 ưu tiên hơn. Đưa cặp này vào phiếu review: ưu tiên MF-03/MF-04/ngang nhau/chưa đủ dữ liệu, cùng lý do về độ khả dĩ tiền điều kiện và hậu quả. **Chưa có quyết định người dùng cho cặp này.** Không tự thêm trọng số hoặc tie-breaker để ép kết quả mong muốn.

## 6. UNKNOWN và khoảng cận

Phân biệt thiếu **context thiết yếu** (scenario, scope, owner, tiền điều kiện/profile) với thiếu điểm có thể chặn trong miền đã biết. Context chưa rõ hoặc input ngoài 1–5 → NEEDS_REVIEW, score/score_range=null; cần sửa đầu vào trước. Known factor phải có rationale/source đúng scope hoặc gắn nhãn minh họa; thiếu căn cứ thì chuyển thành UNKNOWN. Chưa chắc đủ đường kiểm tra được coi là thiếu dữ liệu G, không phải tự tạo một scope đã đầy đủ.

Khi context đủ, với từng yếu tố chưa rõ dùng miền [1,5], hoặc miền hẹp hơn chỉ khi có evidence ràng buộc được reviewer xác nhận. Ví dụ G_range từ danh sách đường ở mục 4. Không dùng giá trị trung bình để giả điền.

```text
E ∈ [Elo,Ehi], F ∈ [Flo,Fhi], G ∈ [Glo,Ghi]
Plo = .4Elo + .6Flo; Phi = .4Ehi + .6Fhi
Llo = 1 + (Plo−1)Glo/5; Lhi = 1 + (Phi−1)Ghi/5
I_total_lo = max(Clo, I_integrity_lo, Alo, Blo); I_total_hi = max(Chi, I_integrity_hi, Ahi, Bhi)
Rlo = Llo × I_total_lo; Rhi = Lhi × I_total_hi
```

Các cận tính bằng tính đơn điệu trên miền 1–5. Range là bao cận trong mô hình, **không phải khoảng tin cậy thống kê**. Nếu yếu tố phụ thuộc nhau, hộp các miền có thể chứa tổ hợp không xảy ra; range được giữ bảo thủ, không tự coi các tổ hợp đều có cùng khả năng.

Kết quả chưa đầy đủ lưu `score=null`, `risk_level=null`, `score_range=[Rlo,Rhi]`, `level_range=[final_level(Rlo,I_total_lo),final_level(Rhi,I_total_hi)]`, `status=NEEDS_REVIEW`, missing_factors và reason/source. `level_range` là cận nhãn, không phải phân phối xác suất; một nhãn duy nhất vẫn không tự đóng review.

**Ngoại lệ suy ra impact:** nếu một chiều đã được xác minh bằng 5, các chiều impact còn lại chưa rõ không thay I_total=5. Nếu E/F/G cũng đầy đủ, cho lưu score xác định cùng `score_determined=true`, score_range=[R,R], nhưng giữ NEEDS_REVIEW và risk_level=null; level_range ghi nhãn tính được. Gaps và các chiều chưa biết vẫn cần review. Không mở ngoại lệ này cho G chưa rõ, kể cả range số tình cờ co lại.

| Ca | Đầu vào | Kết quả tính |
| --- | --- | --- |
| MF-10 | E=5,F=5,G=UNKNOWN; impact=(3,2,1,2) | L=[1.8,5], R=[5.4,15]; score=null, MODERATE–HIGH, NEEDS_REVIEW |
| MF-11 | E=5,F=5,G=2; impact=(3,UNKNOWN,1,2) | I_total=[3,5], R=[7.8,13]; score=null, MODERATE–HIGH |
| MF-12 | E=5,F=5,G=2; impact=(5,UNKNOWN,1,2) | I_total=5, score=13 xác định; NEEDS_REVIEW, level_range=[HIGH,HIGH], risk_level=null |
| MF-13 | E=1,F=1,G=UNKNOWN; impact=(1,1,1,1) | R=[1,1], score=null do G chưa rõ; LOW–LOW, không suy control đạt |
| MF-16 | Có một đường g=4 đã xác minh, một đường UNKNOWN; E=5,F=3, impact=(4,1,1,3) | G=[4,5], R=[12.96,15.2], score=null; giữ các gap của từng đường |

Range giúp reviewer chọn evidence cần thu: MF-10 cần xác minh G; MF-11 cần làm rõ chiều I_integrity; ở MF-12 I_integrity không đổi chỉ số nhưng vẫn có ý nghĩa xử lý hậu quả. Không gọi độ rộng range là mức rủi ro hay mức ưu tiên doanh nghiệp. Trong một case, dùng phân tích yếu tố để gợi ý thu evidence; phải xét mức quan trọng và công sức thu evidence nữa.

## 7. Kiểm tra độ nhạy và hai người chấm G

Phải xét ±1 cho từng E/F/G/C/I_integrity/A/B trên **toàn bộ fixture**, giữ các biến khác cố định. Tại biên 1/5, hướng không hợp lệ ghi BOUNDARY; không ép giá trị về biên rồi gọi đó là một thử nghiệm. Với yếu tố UNKNOWN, ±1 không có điểm gốc: ghi NOT_DEFINED và tính hai đầu miền thay thế; với yếu tố đã biết trong case còn UNKNOWN khác, báo thay đổi range. Báo thay đổi cả R và nhãn sau impact gate. Các biến thể giả định có thể không tương ứng một thay đổi thực tế độc lập, nên chỉ dùng chẩn đoán công thức.

MF-03: ΔR cho G±1 là ±2.24, F±1 là ±1.92, E−1 là −1.28 (E+1 ngoài biên). C±1 làm R đổi ±3.24, I_integrity/A/B±1 hợp lệ không đổi max I_total trong case này. Vì vậy kiểm tra trọng số ±10 điểm phần trăm (±0.64) chưa đủ; ưu tiên review G và impact chi phối. Kết quả đầy đủ nằm trong [báo cáo review](risk-method-review-v0.3.md).

Chuẩn bị hai phiếu A/B với cùng gói case tổng hợp và rubric, không có điểm của người kia. Hai người độc lập ghi coverage, g từng đường, G/range, reason/evidence và thời gian trước khi trao đổi. Sau đó so: tỷ lệ trùng G trong case cả hai có số, phân phối chênh lệch tuyệt đối, chênh lệch ≥2, xung đột số/UNKNOWN, khác biệt về coverage và thay đổi nhãn risk. Case UNKNOWN không bị loại im lặng; báo số lượng/mẫu số. Mọi lệch ≥2 hoặc khác nhãn cần đối chiếu rationale; giữ cả hai lần chấm và kết quả phân xử, không lấy trung bình G tự động. Chưa đặt ngưỡng “độ tin cậy đạt chuẩn” cho mẫu nhỏ.

**Trạng thái: NOT_RUN.** Chưa có hai người chấm thực tế; kiểm tra tính toán hoặc hai lần tự chấm của cùng tác giả không thay thế kiểm tra độc lập. Phiếu tổng hợp cũng không thay thế đánh giá bằng evidence CRM thực tế.

## 8. Trạng thái, version và nguồn

Lưu method/profile, context và tiền điều kiện snapshot, plausibility/horizon, factor values/bounds, template origin/confirmation, coverage và strength theo đường, evidence revisions, vector impact, P/L/I_total/R đầy đủ, score_range/level_range, raw/final level và impact gate reason, actor/time, review decisions. CURRENT cần căn cứ môi trường thật; INHERENT ghi giả định loại bỏ các control cụ thể; ILLUSTRATIVE không đưa vào risk register như kết quả thật. Acceptance/override cần quyền và lý do, không sửa raw result/evidence hoặc che UNKNOWN. Cùng input và version phải tái lập được cùng kết quả; đổi version không ghi đè assessment cũ.

**Nguồn đã kiểm tra ngày 2026-10-10:**

- [NIST SP 800-30 Rev.1, bản final](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf): Task 2-4, trang in 33–34; Phụ lục G, G-1–G-2. G-2 xét khởi phát, G-4 xét hậu quả sau khởi phát, G-5 tổ hợp; Task 2-4 xét safeguards. Đây là căn cứ phân biệt hai nhận định. E/F trong RM-01 không đo khởi phát ngoài điều kiện lab; không gọi công thức 40/60 hay G/5 là công thức NIST. Tài liệu không xác nhận hiệu chuẩn của RM-01.
- [Cox, L. A. Jr. (2008), What's Wrong with Risk Matrices?](https://pubmed.ncbi.nlm.nih.gov/18419665/), Risk Analysis 28(2), 497–512, DOI 10.1111/j.1539-6924.2008.01030.x. Đã đọc abstract trên PubMed, chưa rà soát toàn văn. Bài nêu hạn chế về độ phân giải, đảo thứ hạng, phân bổ nguồn lực và cách diễn giải chủ quan. RM-01 dùng thứ bậc trong phép toán nên cần xem đây là cảnh báo phù hợp; sửa hiển thị và thêm cổng không chứng minh đã khắc phục các hạn chế toán học.
- [MITRE ATT&CK](https://attack.mitre.org/tactics/): metadata hành vi, không là công thức risk. [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html): định hướng quy trình từ giới thiệu công khai; chưa rà soát toàn văn. [IBM risk score](https://www.ibm.com/docs/en/sva/11.0.1?topic=overview-risk-score-calculation): tham khảo về điểm truy cập, không gán mô hình này cho IBM.

Công thức vẫn dùng thứ bậc như khoảng cách để tạo chỉ số quy ước; kết quả không phải xác suất, thiệt hại kỳ vọng hoặc phép tối ưu ngân sách. Max bỏ qua độ rộng hậu quả; conditional bỏ qua khả năng đạt tiền điều kiện; G còn phụ thuộc người chấm; khoảng không khắc phục evidence thiếu. Bước 02 tiếp tục IN_PROGRESS để review các giới hạn, cặp MF-03/MF-04 và phiếu chấm. Không có chứng nhận tuân thủ hoặc triển khai AI/lab từ tài liệu này.

**Chỉnh thuật ngữ ngày 2026-10-10:** thay ký hiệu T trước đây bằng I_integrity, ký hiệu Impact tổng hợp bằng I_total; làm rõ Integrity là thành phần CIA. Đây là chỉnh câu chữ/ký hiệu trong bản DRAFT_REVIEW, không đổi hệ số, ngưỡng hay kết quả tính.
