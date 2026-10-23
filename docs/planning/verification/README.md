# Tái lập kiểm tra RM-01 v0.4

**Ngày:** 2026-10-12; đồng bộ RM-01 v0.4-r3. **Phạm vi:** kiểm tra số học và các quy tắc review bằng dữ liệu tổng hợp. Đây không phải bằng chứng CRM/lab, hiệu chuẩn tham số hoặc kết quả hai người chấm độc lập.

## 1. Bộ tệp cần đọc

| Tệp | Nội dung |
| --- | --- |
| [Phương pháp](../risk-method-v0.4.md) | Công thức và quy tắc đã đóng băng về thiết kế; G chưa được kiểm chứng giữa người chấm |
| [Báo cáo review](risk-method-review-v0.4.md) | Kết quả và giới hạn diễn giải |
| [Fixture chính](risk-method-fixtures-v0.4.json) | 26 ca, kỳ vọng đã lưu và độ nhạy; bản kiểm tra không sửa tệp này |
| [Fixture bổ sung](impact-progress-fixtures-v0.1.json) | 20 ca theo dõi impact (fixture revision v0.1-r2), cặp trọng số MF-03/MF-04, hiển thị cận và bất đồng người chấm |
| [Script kiểm tra độc lập](verify-risk-v0.4.py) | Đọc đầu vào, tính lại và đối chiếu kỳ vọng; chỉ dùng thư viện chuẩn Python |
| [Kết quả lần chạy đã lưu](verification-results-v0.4.json) | Số đếm tính lại, chi tiết kiểm tra và SHA-256 của các tệp đầu vào/script |
| [Phiếu chấm A](../review-forms/risk-g-rating-a-v0.4.md) · [Phiếu chấm B](../review-forms/risk-g-rating-b-v0.4.md) | Hai bản cùng 6 ca, còn trống và NOT_RUN |

## 2. Cách chạy lại

Cần **Python 3.9 trở lên**, không cần cài thêm gói hoặc có mạng. Đặt script và hai tệp fixture JSON cùng một thư mục. Script tìm fixture theo vị trí của chính nó; không phụ thuộc ổ D:, phiên bản cũ, thư mục `work`, CRM hoặc tài khoản bên ngoài.

Mở terminal trong thư mục chứa bộ tệp rồi chạy:

```powershell
python .\verify-risk-v0.4.py
```

Mặc định chỉ đọc tệp và in kết quả. Thành công trả mã thoát **0** và `result: PASS`; bất kỳ sai khác nào trả mã **1**, kèm tên phép kiểm tra lỗi. Script không tạo lại kỳ vọng hoặc tự sửa fixture để đạt PASS.

Muốn lưu kết quả riêng của lần chạy:

```powershell
python .\verify-risk-v0.4.py --json-output .\verification-results-local.json
```

`verification_date` ghi ngày của bộ kiểm tra này, không phải đồng hồ thời gian chạy. SHA-256 gắn kết quả với đúng phiên bản fixture/script đã đọc. Muốn kiểm tra một thay đổi, hãy chạy lại script; PASS đã lưu chỉ mô tả lần chạy với các hash tương ứng.

## 3. Các số đếm được tái lập

| Kiểm tra | Số đếm | Ý nghĩa |
| --- | ---: | --- |
| Ca cố định | 26 | Đối chiếu toàn bộ kỳ vọng tính toán, trạng thái, gaps, miền giá trị và hiển thị |
| Biên phân mức raw | 8 | R25 = 25, 124, 125, 249, 250, 424, 425, 625 |
| Tổ hợp E/F/G/I_total | 625 | Công thức phân số độc lập so với R25 nguyên |
| Cạnh tăng một yếu tố | 2.000 | Điểm và nhãn không giảm khi một đầu vào tăng 1 |
| Hộp khoảng cận | 50.625 | Mỗi trục có 15 khoảng nguyên có thể có trong 1–5 |
| Tổ hợp hoàn thiện trong các hộp | 1.500.625 | Duyệt mọi giá trị hợp lệ trong từng hộp; có lặp giá trị giữa các hộp |
| Hộp co thành một điểm | 675 | Điểm và nhãn xác định; E/F/I_total đều xác định |
| Hộp co điểm nhưng G chưa xác định | 50 | Tất cả đều có E=F=1 |
| Tổ hợp hoàn thiện của fixture | 3.179 | Duyệt các miền E/F/G/C/I_integrity/A/B của các ca hợp lệ |
| Hàng độ nhạy | 182 | 26 ca × 7 yếu tố; gồm các hàng không chạy vì đầu vào/context sai |
| Probe độ nhạy có kết quả | 229 | Hai hướng hợp lệ của các hàng, bỏ hướng vượt biên và hàng không chạy |
| Biến thể trọng số có sẵn | 3 | Kỳ vọng MF-03 trong fixture chính |

Độ nhạy G tổng hợp là giả định để kiểm tra phép tính; không sửa evidence từng đường. Giữ nguyên gaps và trạng thái NEEDS_REVIEW của baseline trong probe. Các probe không chứng minh treatment đã thành công.

**Kiểm tra bổ sung được đếm riêng:** 20 ca impact progress, 3 cặp trọng số với 6 phép tính cho MF-03/MF-04, 2 ca hiển thị và 1 ca bất đồng người chấm. Không cộng chúng vào con số 26 ca chính.

## 4. Các điểm cần đọc đúng

- Với profile 40/60 hiện tại, cổng impact chỉ đổi nhãn raw ở đúng hai bộ `(E,F,G,I_total)`: `(5,5,5,1)` và `(5,5,5,2)`. Đây là hệ quả của tham số hiện tại; thay ngưỡng phải chạy lại kiểm tra.
- Trọng số E/F 30/70 cho MF-03=12.32 < MF-04=12.64; 40/60 cho 12.96 > 12.32; 50/50 cho 13.6 > 12.0. Thứ tự số học đảo khi trọng số thay đổi; không tự biến bảng này thành quyết định ưu tiên xử lý.
- Cận chính xác `[3.72,4.96]` có thể xuất hiện trong profile: E=1, F=2, G=2, I_total∈[3,4]. Hiển thị `[3.7,5.0]` nhưng nhãn vẫn `[LOW,LOW]` từ giá trị chính xác.
- `9.96→10.0` là kiểm tra riêng cho hàm làm tròn cận trên. **9.96 không phải điểm đạt được trên miền đầu vào nguyên của profile v0.4.** Điểm lớn nhất nhỏ hơn 10 là 9.8; lớn nhất nhỏ hơn 17 là 16.8. Không trình bày ca formatter này như một assessment hợp lệ của profile hiện tại.
- MF-04 giảm riêng C, Integrity hoặc B từ 4 xuống 3: impact có tiến bộ, R vẫn 12.32. Giảm cả ba: R=9.24. `impact_progress` ghi từng chiều, không cộng các chiều hoặc suy phần trăm giảm thiệt hại.
- `comparison_review_status` trong fixture bổ sung chỉ là trạng thái review phép so sánh impact. IP-15 có impact tiến bộ đã xác minh, trong khi G còn UNKNOWN và hai assessment gốc vẫn NEEDS_REVIEW. Phép so sánh không nâng trạng thái của assessment hoặc đóng control gap.
- IP-16 tách việc bổ sung evidence cho Integrity từ UNKNOWN thành 3 khỏi việc cải thiện hậu quả: C giảm đã xác minh, Integrity vẫn NOT_COMPARABLE so với snapshot gốc; tổng phép so là INCOMPLETE. Gap evidence được ghi là đã bổ sung, không sửa ngược snapshot UNKNOWN hoặc suy Integrity đã giảm.
- `treatment_attribution=SUPPORTED` chỉ áp dụng cho những chiều đã so sánh được, với liên kết treatment/retest giả định đã xác nhận. `REVIEW_REQUIRED` giữ yêu cầu xác minh liên kết; một chênh lệch điểm hoặc vector tự nó không chứng minh nhân quả.
- Một ca bất đồng G vẫn cho điểm duy nhất khi E=F=1; trạng thái vẫn NEEDS_REVIEW. Không lấy trung bình ý kiến hoặc nhân confidence vào R.

## 5. Giới hạn của PASS

Verifier tính các score chính bằng `fractions.Fraction` từ biểu thức P/L/R, sau đó đối chiếu công thức R25. Miền unknown được dựng lại từ **đầu vào** trước khi duyệt; không tin sẵn miền hoặc số đếm ghi trong `expected`/`validation`.

PASS xác nhận các tệp này nhất quán với những quy tắc được kiểm tra. Nó không chứng minh trọng số hoặc rubric phù hợp mọi SME; không xác nhận hiệu lực control; không thay thế chấm G độc lập bằng phiếu A/B. Hai phiếu vẫn trống, chưa có số liệu đồng thuận.

## 6. Bổ sung ở r3

- `verified_worsening=true` khi có UP đã xác minh trong context tương thích, kể cả INCOMPLETE. False chỉ khi đủ bốn chiều so sánh được và không có UP; còn thiếu dữ liệu mà chưa có UP hoặc context không tương thích thì null.
- `impact_summary_before/after` có I_total/range và số chiều bằng max/range. Max xác định không chứng minh số chiều bằng max cũng xác định; số đếm chỉ mô tả, không cộng vào R hay dùng để xếp hạng. IP-17…IP-20 kiểm tra các trường hợp thiếu evidence, max=5, context khác và điểm gợi ý chưa xác minh.
- Fixture chính giữ nguyên; fixture bổ sung có `fixture_revision=v0.1-r2`, quy tắc tổng hợp IMPACT-PROGRESS-v0.1 không đổi. Verifier và hash kết quả đã cập nhật. Bundle cũ được giữ trong [history/risk-v0.4-r2.zip](../history/risk-v0.4-r2.zip).
- Hai phiếu A/B thuộc VALID-G-01 ở bước 06, vẫn NOT_RUN. Độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng; việc đóng băng thiết kế bước 02 không thay trạng thái này.
