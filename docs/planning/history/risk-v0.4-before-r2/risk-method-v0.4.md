# RM-01 v0.4 — Chỉ số risk có điều kiện và review evidence

**Ngày:** 2026-10-10. **Cập nhật review:** 2026-10-11. **Trạng thái:** DRAFT_REVIEW; bước 02 IN_PROGRESS. Bản này thay v0.3 cho công việc review hiện tại; các phiên bản cũ được giữ làm lịch sử. Người dùng đã đồng ý áp dụng các sửa đổi và cách diễn giải ở bản này ngày 2026-10-10; điều đó chưa hoàn tất mọi điều kiện của bước 02. Chưa có kết quả lab, hiệu chuẩn SME hoặc kết quả hai người chấm độc lập.

Tài liệu liên quan: [control/evidence](../../control-evidence-v0.1.md), [ca kiểm thử control](../../control-test-cases-v0.1.md), [kế hoạch](execution-plan-v0.1.md), [fixture và kỳ vọng](../../verification/risk-method-fixtures-v0.4.json), [phân tích độ nhạy/kiểm tra](risk-method-review-v0.4.md), [phiếu chấm độc lập A](../../review-forms/risk-g-rating-a-v0.4.md), [phiếu chấm độc lập B](../../review-forms/risk-g-rating-b-v0.4.md).

## 1. Mục đích và cách dùng register

R chủ yếu dùng để đối chiếu **trước/sau treatment của cùng scenario, tiền điều kiện và phạm vi hậu quả**, cùng method/profile. Nếu môi trường, năng lực đối thủ, scope hoặc cách đặt tiền điều kiện thay đổi, phải ghi rõ; không quy toàn bộ chênh lệch R cho treatment. Lưu các yếu tố thay đổi và evidence tương ứng. Giảm điểm không đồng nghĩa đo được tỷ lệ giảm tổn thất.

Profile `CONDITIONAL-BASE-v0.4` giả định tiền điều kiện đã đúng. Với SC-01 đã tới CRM qua VPN và biết mật khẩu; SC-02 đã có phiên đọc, E thường là 5. Khi E=5, P=2+0.6F; việc E không phân biệt hai case là giới hạn được thừa nhận. E chỉ mô tả cơ hội hành động còn lại trong trạng thái đã giả định, không đại diện tần suất năm. Không tự hạ E để làm đẹp điểm.

Register vẫn chứa SC-01 và SC-02, kể cả NEEDS_REVIEW. Mặc định nhóm theo scenario và lịch sử treatment; không tự xếp toàn bộ scenario theo R. Khi reviewer muốn so sánh chéo, phải hiển thị cạnh nhau: tiền điều kiện, `precondition_plausibility`, kỳ xem xét, C/I_integrity/A/B, evidence gaps, control failures và R/range. Kết quả ưu tiên là quyết định reviewer có lý do; không suy thứ tự từ R đơn lẻ hoặc nhân nhãn độ khả dĩ vào R. Với score_range, không dùng cận trên, cận dưới hay trung điểm để xếp hạng.

`precondition_plausibility` đánh giá khả năng các tiền điều kiện đồng thời tồn tại **ngoài giả định lab**, theo một kỳ xem xét chung (đề xuất 12 tháng nếu SME xác nhận):

| Nhãn | Căn cứ cần có |
| --- | --- |
| LOW | Có trở ngại cụ thể khiến tập tiền điều kiện khó đồng thời đạt; không chỉ dựa vào chưa thấy sự cố |
| MEDIUM | Có đường khả thi để đạt tập điều kiện, nhưng chưa đủ căn cứ cho LOW/HIGH |
| HIGH | Có evidence gần bối cảnh về điều kiện thường xuyên sẵn có hoặc đã nhiều lần xảy ra |
| UNKNOWN | Chưa có căn cứ, chưa chọn kỳ xem xét hoặc các nhận định mâu thuẫn |

Mỗi nhãn có reason/source, reviewer và as_of/horizon; đây là nhận định riêng, không phải xác suất đã hiệu chuẩn. Chỉ giả định biết mật khẩu trong SC-01 không đủ để gán HIGH cho khả năng mật khẩu thực tế bị lộ. Nếu nhãn UNKNOWN, so sánh chéo chỉ là review tạm, không là xếp hạng tự động đã xác nhận.

## 2. Công thức và quy tắc tính chính xác

Profile `CONDITIONAL-BASE-v0.4`. Mọi điểm đầu vào và đầu mút miền phải là **số nguyên thuộc {1,2,3,4,5}**. Thang điểm vẫn là thứ bậc; phép tính chính xác chỉ bảo đảm tái lập kết quả, không chứng minh độ chính xác đo lường.

```text
P = 0.40 × E + 0.60 × F
L = 1 + (P − 1) × G / 5
I_total = max(C, I_integrity, A, B)
R = L × I_total

R25 = I_total × (25 + (2E + 3F − 5) × G)
R = R25 / 25

raw_level(R25):
  R25 < 125 → LOW
  R25 < 250 → MODERATE
  R25 < 425 → HIGH
  còn lại  → CRITICAL

final_level(R25, I_total):
  I_total = 1 → LOW
  I_total = 2 → min(raw_level(R25), MODERATE)
  I_total ≥ 3 → raw_level(R25)
```

Thứ tự nhãn: LOW < MODERATE < HIGH < CRITICAL. Chỉ áp dụng các ngưỡng sau khi đầu vào hợp lệ; R25 thuộc [25,625]. **Bắt buộc dùng số nguyên R25 khi lưu kết quả chuẩn, so sánh, kiểm tra hai cận bằng nhau và phân mức.** R là biểu diễn chính xác của R25/25; không so số thực bằng epsilon hoặc dùng số hiển thị để quyết định nhãn. Nếu định dạng lưu cần R dạng thập phân, dùng biểu diễn thập phân chính xác hoặc dựng từ R25; R25 là căn cứ tái lập.

R giữ nguyên qua cổng impact. Lưu `raw_level`, `risk_level` và `impact_gate_reason`. Ví dụ L=5/I_total=1: R=5, raw MODERATE nhưng final LOW; L=5/I_total=2: R=10, raw HIGH nhưng final MODERATE. Giao diện giải thích cổng impact khi nhãn cuối thấp hơn nhãn raw. Điểm thấp không làm một control bắt buộc đã thất bại trở thành đạt và không tự chấp nhận risk.

### Hiển thị

- Điểm xác định: **cắt xuống một chữ số thập phân**, luôn kèm nhãn cuối và vector C/I_integrity/A/B. Ví dụ R=9.72 → `9.7 · MODERATE`; MF-03 R=12.96 → `12.9 · HIGH`; MF-04 R=12.32 → `12.3 · HIGH`.
- Range: cận dưới cắt xuống, cận trên làm tròn lên đến một chữ số thập phân. Ví dụ [12.96,15.2] hiển thị `[12.9,15.2]`. Cận hiển thị chỉ bao cận; nhãn tính từ cận chính xác, kể cả khi cận trên hiển thị chạm ngưỡng mới.
- Dùng phép chia nguyên: số phần mười của điểm/cận dưới = `floor(2 × R25 / 5)`; của cận trên = `ceil(2 × R25 / 5)`. Định dạng các số nguyên đó thành một chữ số thập phân. Chi tiết tính cho phép xem R chính xác.
- Các ngưỡng raw là số nguyên nên cắt xuống một chữ số thập phân không đổi raw_level. Cổng impact vẫn có thể làm `10.0 · MODERATE`; lý do là impact, không phải làm tròn. Một chữ số thập phân không biến thang thứ bậc thành thang đo liên tục đã hiệu chuẩn.

### Bất biến và hệ quả được giữ trong profile này

```text
R ∈ [1,25]
R không giảm khi tăng bất kỳ yếu tố nào, giữ các yếu tố còn lại cố định
I_total ≤ 2 ⇒ risk_level ≤ MODERATE
CRITICAL ⇒ I_total ≥ 4
G = 1 ⇒ L ≤ 1.8 ⇒ R ≤ 9
P = 1 ⇒ L = 1 bất kể G
```

**Quyết định thiết kế được chấp nhận cho v0.4:** giữ công thức như một chỉ số rủi ro còn lại có điều kiện, có mức sàn dương. Khi G=1, ngay cả I_total=5 cũng không lên HIGH. G=1 chỉ có nghĩa tiêu chí trọng yếu đã được xác minh đạt trong scope, cấu hình, đường kiểm tra và thời điểm đã ghi; không khẳng định control hoàn hảo hoặc mọi bypass đều bất khả thi. Vector impact và chiều bằng 5 vẫn phải nổi bật để reviewer cân nhắc hậu quả, phạm vi và việc xử lý. MODERATE không tự đóng review, chấp nhận risk hay bỏ qua control failure.

P=1 xảy ra khi E=F=1; lúc đó điểm không phụ thuộc G. Việc biết điểm trong trường hợp này không cung cấp evidence về G. Mọi gap còn lại vẫn được giữ. Nếu sau này yêu cầu “impact cực lớn luôn HIGH dù control tốt”, cần thay quy tắc và tạo version mới; không âm thầm đổi nhãn.

40/60, G/5, cổng impact và các ngưỡng là tham số/quy tắc do dự án đề xuất, **chưa hiệu chuẩn**. G/5 không phải phần trăm hiệu lực control. Thay tham số hoặc quy tắc tính/phân mức phải tạo method/profile version mới và giữ snapshot cũ.

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

Nếu không phân biệt được cản trở đáng kể/nhỏ bằng evidence, giữ `g=UNKNOWN` hoặc ghi bất đồng chờ xử lý; không ép chọn 3 hay 4. VERIFIED_UNCOVERED → g=5. UNKNOWN coverage/strength → mặc định miền g=[1,5] cho tính cận; miền hẹp hơn cần evidence ràng buộc được reviewer xác nhận. COVERED chỉ nói đã xét coverage, không tự tương đương g=1.

`G=max(g_path)` áp dụng cho **các đường thay thế dẫn đến cùng sự kiện trong cùng scope**. Không lấy max này để gộp các bước nối tiếp trong một chuỗi tấn công hoặc các lớp kiểm soát trên cùng đường; các lớp đó được xét khi chấm sức cản g của đường.

Mỗi đường có miền `[g_lo,g_hi]`: điểm đã biết là `[g,g]`; UNKNOWN mặc định `[1,5]`, chỉ thu hẹp khi evidence ràng buộc được reviewer xác nhận. Tính `G_lo=max(g_lo)` và `G_hi=max(g_hi)`. Khi mọi đường đã biết, hai cận bằng max thực tế, không đặt cận trên mặc định 5. Nếu danh sách đường chưa được xác minh đầy đủ, giữ một phần phạm vi chưa đánh giá với miền `[1,5]`; không coi tập đường rỗng là G=1. Đường N/A chỉ được loại khi có lý do đúng scope được reviewer xác nhận.

**Cùng một quy tắc xác định giá trị cho G và impact:** nếu hai cận bằng nhau thì aggregate đã xác định. Đặc biệt, một đường VERIFIED_UNCOVERED với g=5 cùng một đường UNKNOWN cho G=[5,5], nên **G=5 đã xác định**. UNKNOWN trên đường còn lại vẫn là EVIDENCE_GAP và vẫn làm assessment NEEDS_REVIEW. G có số không chứng minh coverage đầy đủ. Tổng quát hơn, đường đã biết g=3 cùng một đường chưa rõ nhưng có cận được xác nhận [1,2] cũng cho G=3.

Một bypass đã xác minh vẫn tạo CONTROL_GAP; xử lý theo vi phạm và phạm vi của nó, không chờ đóng các evidence gap khác. Ví dụ minh họa MF-17: E=F=5, các đường g=(5,UNKNOWN), impact=(3,2,1,2) → G=5, R=15, HIGH, NEEDS_REVIEW; giữ đồng thời control failure và đường recovery chưa có evidence.

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

Max không biểu diễn độ rộng hậu quả. Bắt buộc giữ vector, các chiều bằng mức lớn nhất và mô tả phạm vi. MF-03 có (4,1,1,3), R=12.96; MF-04 có (4,4,3,4), R=12.32. Cả hai HIGH. Việc MF-04 có hậu quả rộng hơn chưa làm R cao hơn vì P khác nhau và max chỉ giữ I_total=4. Không tự kết luận MF-03 ưu tiên hơn. **Review thiết kế đã hoàn tất bởi trợ lý ngày 2026-10-11 theo yêu cầu người dùng.** Hai ca cùng nhóm HIGH. Nếu cần thứ tự minh họa, đề xuất MF-04 trước với giả định tiền điều kiện có độ khả dĩ tương đương và lựa chọn ưu tiên hậu quả rộng hơn trong cùng nhóm HIGH. Đây là nhận xét có điều kiện của reviewer cho cặp ca này; E/F khác nhau nên không thể suy MF-04 trội hơn trên toàn bộ đầu vào. Độ khả dĩ tiền điều kiện thực tế vẫn UNKNOWN; thứ tự xử lý thực tế chưa xác định. Không yêu cầu người dùng tự chấm lại fixture. Xem rationale chi tiết tại báo cáo review mục 4. Không tự thêm trọng số hoặc tie-breaker để ép kết quả mong muốn.

## 6. UNKNOWN, khoảng cận và điểm đã xác định

Tách hai câu hỏi: **đã xác định được con số/nhãn chưa** (`score_determined`) và **hồ sơ đã đủ căn cứ để hoàn tất đánh giá chưa** (`status`). Điểm xác định vẫn có thể đi cùng NEEDS_REVIEW.

### 6.1. Kiểm tra đầu vào trước khi tính

Thiếu context thiết yếu (scenario, scope, owner, tiền điều kiện/profile), điểm hoặc đầu mút miền không phải số nguyên 1–5, miền đảo ngược hay dữ liệu mâu thuẫn chưa giải quyết → `status=NEEDS_REVIEW`, `score_determined=false`; score, R25, nhãn và các range đều null. Ghi validation issues để sửa đầu vào; không tự kẹp giá trị về biên.

Known factor phải có rationale/source đúng scope và xác nhận phù hợp, hoặc được gắn nhãn giả định ILLUSTRATIVE trong bài tính mẫu. Template PROPOSED, source chưa xác minh hoặc điểm chưa có căn cứ không được dùng như điểm đã biết của assessment CURRENT: chuyển phần đó thành UNKNOWN và ghi lý do. Miền hẹp chỉ được dùng khi **chính căn cứ ràng buộc miền đã được reviewer xác nhận**; gợi ý chưa xác nhận không làm hẹp [1,5]. Thiếu bằng chứng về đường đã biết thuộc scope là thiếu dữ liệu G; thiếu chính định nghĩa scenario/scope là thiếu context và chặn tính range.

### 6.2. Miền của từng yếu tố và max

- Yếu tố đã biết x: `[x,x]`.
- E/F chưa rõ: `[1,5]`, hoặc cận hẹp hơn có căn cứ được xác nhận.
- Mỗi đường của G và mỗi chiều impact dùng cùng nguyên tắc miền trên. UNKNOWN chưa có căn cứ hẹp giữ `[1,5]`.

```text
G_lo = max(g_lo của các đường áp dụng)
G_hi = max(g_hi của các đường áp dụng)
I_total_lo = max(C_lo, I_integrity_lo, A_lo, B_lo)
I_total_hi = max(C_hi, I_integrity_hi, A_hi, B_hi)
```

Khi còn ít nhất một thành phần UNKNOWN và tất cả UNKNOWN dùng miền [1,5], có thể viết tắt cận aggregate là `[max(các giá trị đã biết,1),5]`. Công thức tổng quát ở trên vẫn là quy tắc chuẩn: khi mọi thành phần đã biết hoặc có cận hẹp, cận trên không nhất thiết là 5. Nếu cận dưới bằng 5 thì cận trên cũng bằng 5; aggregate đã xác định bằng 5 cho **cả G lẫn I_total**, còn thành phần chưa rõ vẫn ghi gap. Không sửa UNKNOWN của từng đường/chiều thành một giá trị tự đoán.

### 6.3. Tính cận chính xác và kết quả

```text
R25_lo = I_total_lo × (25 + (2E_lo + 3F_lo − 5) × G_lo)
R25_hi = I_total_hi × (25 + (2E_hi + 3F_hi − 5) × G_hi)
score_range = [R25_lo/25, R25_hi/25]
level_range = [final_level(R25_lo,I_total_lo),
               final_level(R25_hi,I_total_hi)]

Nếu R25_lo = R25_hi:
  score_determined = true
  R25 = R25_lo; score = R25 / 25
  raw_level = raw_level(R25)
  risk_level = final_level(R25,I_total)
  điền impact_gate_reason; giữ score_range=[score,score]
Nếu R25_lo < R25_hi:
  score_determined = false
  R25 = score = raw_level = risk_level = null
  giữ R25_range, score_range, level_range và lý do chưa xác định
```

Trong miền độc lập hợp lệ của profile, L luôn dương; nếu hai cận R bằng nhau thì I_total cũng đã xác định, nên nhãn sau cổng impact và lý do cổng đều xác định. Với trường hợp chưa có điểm duy nhất, có thể lưu raw_level_range và các cổng impact có thể áp dụng để giải thích, không giả điền một kết luận duy nhất.

Các cận dựa vào tính đơn điệu. Đây là bao cận của mô hình, **không phải khoảng tin cậy thống kê**. Nếu yếu tố phụ thuộc nhau, hộp các miền có thể chứa tổ hợp không xảy ra; giữ bao cận bảo thủ và không giả định các tổ hợp có cùng khả năng. Không dùng cận dưới, cận trên hoặc trung điểm để xếp hạng scenario. Hai cận nhãn giống nhau không có nghĩa hai cận điểm giống nhau: MF-16 vẫn có R=[12.96,15.2], HIGH–HIGH và score=null.

### 6.4. Trạng thái review độc lập với con số

`EVALUATED` chỉ khi context hợp lệ, các input/miền và nguồn đã được xác nhận theo loại đánh giá, danh sách đường đã được rà soát, và không còn yếu tố hoặc đường UNKNOWN hay việc xác nhận còn thiếu. Với CURRENT, phải có căn cứ của môi trường đang đánh giá; không nâng trạng thái chỉ vì có số từ template. Các fixture ILLUSTRATIVE chỉ mô phỏng trạng thái theo giả định bài tính, không tạo assessment CRM thực tế.

Còn UNKNOWN/gap cần review → `NEEDS_REVIEW`, kể cả `score_determined=true`. Giữ `missing_factors`, `missing_paths`, reference/source, lý do và việc xác nhận còn thiếu. Có thể ghi `determination_reasons` để giải thích aggregate bão hòa ở 5, max đã bị chặn bởi thành phần đã biết, hoặc P=1 khiến điểm không phụ thuộc G. Không đánh dấu review hoàn tất hay tự đóng gap từ `score_determined`.

| Ca | Đầu vào | Kết quả chính xác theo v0.4 |
| --- | --- | --- |
| MF-10 | E=5,F=5,G=UNKNOWN; impact=(3,2,1,2) | R=[5.4,15], score=null, MODERATE–HIGH, NEEDS_REVIEW |
| MF-11 | E=5,F=5,G=2; impact=(3,UNKNOWN,1,2) | I_total=[3,5], R=[7.8,13], score=null, MODERATE–HIGH, NEEDS_REVIEW |
| MF-12 | E=5,F=5,G=2; impact=(5,UNKNOWN,1,2) | I_total=5, R25=325, score=13, risk_level=HIGH, score_determined=true, NEEDS_REVIEW |
| MF-13 | E=1,F=1,G=UNKNOWN; impact=(1,1,1,1) | R25=25, score=1, risk_level=LOW, score_determined=true, NEEDS_REVIEW; không suy control đạt |
| MF-16 | E=5,F=3; đường g=4 và UNKNOWN; impact=(4,1,1,3) | G=[4,5], R=[12.96,15.2], score=null, HIGH–HIGH, NEEDS_REVIEW |
| MF-17 | E=F=5; đường g=5 và UNKNOWN; impact=(3,2,1,2) | G=5, R25=375, score=15, risk_level=HIGH, score_determined=true, NEEDS_REVIEW |

MF-10 cần evidence G; MF-11 cần làm rõ I_integrity. MF-12 vẫn cần review Integrity dù điểm không đổi; MF-17 cần xử lý bypass đã biết và bổ sung evidence recovery. Range giúp xác định phần thông tin còn thiếu trong từng case; độ rộng range không tự là mức ưu tiên doanh nghiệp. Reviewer còn xét hậu quả, vi phạm đã biết và công sức thu evidence.

## 7. Kiểm tra độ nhạy và hai người chấm G

Phải xét ±1 cho từng E/F/G/C/I_integrity/A/B trên **toàn bộ fixture**, giữ các biến khác cố định. Tại biên 1/5, hướng không hợp lệ ghi BOUNDARY; không ép giá trị về biên rồi gọi đó là một thử nghiệm. Với yếu tố UNKNOWN, ±1 không có điểm gốc: ghi NOT_DEFINED và tính hai đầu miền thay thế; với yếu tố đã biết trong case còn UNKNOWN khác, báo thay đổi range. Báo thay đổi cả R và nhãn sau impact gate. Các biến thể giả định có thể không tương ứng một thay đổi thực tế độc lập, nên chỉ dùng chẩn đoán công thức.

MF-03: ΔR cho G±1 là ±2.24, F±1 là ±1.92, E−1 là −1.28 (E+1 ngoài biên). C±1 làm R đổi ±3.24, I_integrity/A/B±1 hợp lệ không đổi max I_total trong case này. Vì vậy kiểm tra trọng số ±10 điểm phần trăm (±0.64) chưa đủ; ưu tiên review G và impact chi phối. Kết quả đầy đủ nằm trong [báo cáo review](risk-method-review-v0.4.md).

Chuẩn bị hai phiếu A/B với cùng gói case tổng hợp và rubric, không có điểm của người kia. Hai người độc lập ghi coverage, g từng đường, G/range, các đường UNKNOWN/gap còn lại, reason/evidence và thời gian trước khi trao đổi. G xác định không được xem là hồ sơ đủ: đối chiếu riêng con số và tình trạng evidence. Sau đó so: tỷ lệ trùng G trong case cả hai có số, phân phối chênh lệch tuyệt đối, chênh lệch ≥2, xung đột số/UNKNOWN, khác biệt về coverage và thay đổi nhãn risk. Case UNKNOWN không bị loại im lặng; báo số lượng/mẫu số. Mọi lệch ≥2 hoặc khác nhãn cần đối chiếu rationale; giữ cả hai lần chấm và kết quả phân xử, không lấy trung bình G tự động. Chưa đặt ngưỡng “độ tin cậy đạt chuẩn” cho mẫu nhỏ.

**Trạng thái: NOT_RUN.** Chưa có hai người chấm thực tế; kiểm tra tính toán hoặc hai lần tự chấm của cùng tác giả không thay thế kiểm tra độc lập. Phiếu tổng hợp cũng không thay thế đánh giá bằng evidence CRM thực tế.

## 8. Trạng thái, version và nguồn

Lưu R25/R25_range nguyên, score_determined, determination_reasons, missing_factors/missing_paths và việc xác nhận còn thiếu; lưu method/profile, context và tiền điều kiện snapshot, plausibility/horizon, factor values/bounds, template origin/confirmation, coverage và strength theo đường, evidence revisions, vector impact, P/L/I_total/R đầy đủ, score_range/level_range, raw/final level và impact gate reason, actor/time, review decisions. CURRENT cần căn cứ môi trường thật; INHERENT ghi giả định loại bỏ các control cụ thể; ILLUSTRATIVE không đưa vào risk register như kết quả thật. Acceptance/override cần quyền và lý do, không sửa raw result/evidence hoặc che UNKNOWN. Cùng input và version phải tái lập được cùng kết quả; đổi version không ghi đè assessment cũ.

**Nguồn đã kiểm tra ngày 2026-10-10:**

- [NIST SP 800-30 Rev.1, bản final](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf): Task 2-4, trang in 33–34; Phụ lục G, G-1–G-2. G-2 xét khởi phát, G-4 xét hậu quả sau khởi phát, G-5 tổ hợp; Task 2-4 xét safeguards. Đây là căn cứ phân biệt hai nhận định. E/F trong RM-01 không đo khởi phát ngoài điều kiện lab; không gọi công thức 40/60 hay G/5 là công thức NIST. Tài liệu không xác nhận hiệu chuẩn của RM-01.
- [Cox, L. A. Jr. (2008), What's Wrong with Risk Matrices?](https://pubmed.ncbi.nlm.nih.gov/18419665/), Risk Analysis 28(2), 497–512, DOI 10.1111/j.1539-6924.2008.01030.x. Đã đọc abstract trên PubMed, chưa rà soát toàn văn. Bài nêu hạn chế về độ phân giải, đảo thứ hạng, phân bổ nguồn lực và cách diễn giải chủ quan. RM-01 dùng thứ bậc trong phép toán nên cần xem đây là cảnh báo phù hợp; sửa hiển thị và thêm cổng không chứng minh đã khắc phục các hạn chế toán học.
- [MITRE ATT&CK](https://attack.mitre.org/tactics/): metadata hành vi, không là công thức risk. [ISO/IEC 27005:2022](https://www.iso.org/standard/80585.html): định hướng quy trình từ giới thiệu công khai; chưa rà soát toàn văn. [IBM risk score](https://www.ibm.com/docs/en/sva/11.0.1?topic=overview-risk-score-calculation): tham khảo về điểm truy cập, không gán mô hình này cho IBM.

Công thức vẫn dùng thứ bậc như khoảng cách để tạo chỉ số quy ước; kết quả không phải xác suất, thiệt hại kỳ vọng hoặc phép tối ưu ngân sách. Max bỏ qua độ rộng hậu quả; conditional bỏ qua khả năng đạt tiền điều kiện; G còn phụ thuộc người chấm; khoảng không khắc phục evidence thiếu. Review thiết kế MF-03/MF-04 đã có kết luận có điều kiện của trợ lý; bước 02 tiếp tục IN_PROGRESS để hoàn tất hoặc chốt phạm vi kiểm tra người chấm G. Dữ liệu thực tế và hiệu chuẩn SME vẫn chưa có. Không có chứng nhận tuân thủ hoặc triển khai AI/lab từ tài liệu này.

**Chỉnh thuật ngữ ngày 2026-10-10:** thay ký hiệu T trước đây bằng I_integrity, ký hiệu Impact tổng hợp bằng I_total; làm rõ Integrity là thành phần CIA. Đây là chỉnh câu chữ/ký hiệu trong bản DRAFT_REVIEW, không đổi hệ số, ngưỡng hay kết quả tính.

## 9. Thay đổi từ v0.3 và trạng thái áp dụng

- Dùng cùng quy tắc max và cận cho G/impact; aggregate đã xác định không xóa UNKNOWN ở thành phần.
- Bỏ các ngoại lệ riêng MF-12/MF-13; nếu hai cận R25 bằng nhau thì điền cả điểm, raw/final level và lý do cổng, vẫn giữ NEEDS_REVIEW khi hồ sơ thiếu.
- Tính/lưu/phân mức bằng R25 nguyên, hiển thị điểm cắt xuống một chữ số thập phân và range làm tròn ra ngoài.
- Ghi rõ hệ quả G=1 ⇒ R≤9, CRITICAL ⇒ I_total≥4, P=1 ⇒ L=1; giữ công thức và cách diễn giải rủi ro còn lại có điều kiện theo đồng ý ngày 2026-10-10.
- Giữ nguyên hệ số, thang điểm, cổng impact, ngưỡng, CIA+B, ranh giới F/G và phạm vi so sánh. Phiếu A/B được chuyển sang v0.4 để dùng đúng rubric, vẫn trống và NOT_RUN.

Các sửa đổi đã được người dùng cho phép áp dụng; không tiếp tục ghi chúng là đang chờ phê duyệt. Review thiết kế MF-03/MF-04 đã hoàn tất ngày 2026-10-11; chưa xác định ưu tiên doanh nghiệp khi chưa có dữ liệu thực tế. Bản phương pháp vẫn DRAFT_REVIEW vì kiểm tra G bởi hai người chưa hoàn tất hoặc chưa chốt lại phạm vi kiểm tra. Bước 02 IN_PROGRESS; bước 03–06 chưa bắt đầu. Các kiểm tra số học trong báo cáo v0.4 không chứng minh hiệu lực control hoặc hiệu chuẩn tham số.
