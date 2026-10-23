# Review và kiểm tra RM-01 v0.4

**Ngày:** 2026-10-10. **Cập nhật review:** 2026-10-12, revision v0.4-r3. **Trạng thái:** DESIGN_FROZEN; bước 02 COMPLETE về thiết kế. VALID-G-01 ở bước 06 còn NOT_RUN; độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng.

Nguồn quy tắc: [RM-01 v0.4](risk-method-v0.4.md); fixture JSON. Đây là kiểm tra phép tính thiết kế. Mọi trạng thái evidence/xác nhận trong fixture là giả định tổng hợp; không có kết quả CRM/lab, hiệu chuẩn SME hoặc người chấm độc lập. EVALUATED trong bảng chỉ là trạng thái mà đầu vào giả định đầy đủ sẽ cho ra.

## 1. Các thay đổi đã kiểm tra

- Tính/lưu/phân mức bằng số nguyên R25; R = R25/25. Các chuỗi thập phân trong JSON chỉ là biểu diễn chính xác để đọc, không phải đầu vào phân mức.
- G và impact cùng lấy max của cận từng thành phần. Max đã xác định có thể là 5 do bão hòa hoặc nhỏ hơn 5 khi mọi cận còn lại bị một giá trị đã biết chi phối.
- R25_lo = R25_hi thì điền score, raw_level, risk_level và impact_gate_reason. Gaps vẫn giữ NEEDS_REVIEW. Một level_range chỉ có HIGH không đủ để xác định score.
- Số đọc được cắt xuống 1 chữ số thập phân; range bao ngoài với cận dưới cắt xuống/cận trên làm tròn lên. Nhãn luôn tính từ R25 chính xác.
- Template PROPOSED và cận chưa được xác nhận không trở thành điểm/cận đã biết. Thiếu context, input không nguyên/ngoài miền hoặc cận sai đều không tính range.

| Ca | Nội dung | R chính xác · nhãn | Hiển thị | Trạng thái |
| --- | --- | --- | --- | --- |
| MF-01 | SC-01: control hiệu lực giả định | 7.8 · MODERATE | 7.8 · MODERATE | EVALUATED |
| MF-02 | SC-01: bypass giả định | 15 · HIGH | 15.0 · HIGH | EVALUATED |
| MF-03 | SC-02: đường chuyển giả định | 12.96 · HIGH | 12.9 · HIGH | EVALUATED |
| MF-04 | Đặc quyền: kiểm tra biểu diễn | 12.32 · HIGH | 12.3 · HIGH | EVALUATED |
| MF-05 | SC-01 chưa có evidence G/impact | [1.8, 25] · LOW–CRITICAL · REVIEW | [1.8, 25.0] · LOW–CRITICAL · REVIEW | NEEDS_REVIEW |
| MF-06 | Cận dưới toàn bộ yếu tố | 1 · LOW | 1.0 · LOW | EVALUATED |
| MF-07 | Cận trên toàn bộ yếu tố | 25 · CRITICAL | 25.0 · CRITICAL | EVALUATED |
| MF-08 | Impact gate I_total=1 | 5 · LOW | 5.0 · LOW | EVALUATED |
| MF-09 | Impact gate I_total=2 | 10 · MODERATE | 10.0 · MODERATE | EVALUATED |
| MF-10 | Chỉ G chưa rõ | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15.0] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-11 | I_integrity chưa rõ, impact chưa xác định | [7.8, 13] · MODERATE–HIGH · REVIEW | [7.8, 13.0] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-12 | C=5 hấp thụ I_integrity chưa rõ | 13 · HIGH · REVIEW | 13.0 · HIGH · REVIEW | NEEDS_REVIEW |
| MF-13 | P=1: G chưa rõ nhưng score xác định | 1 · LOW · REVIEW | 1.0 · LOW · REVIEW | NEEDS_REVIEW |
| MF-14 | Thiếu owner/context thiết yếu | MISSING_ESSENTIAL_CONTEXT | MISSING_ESSENTIAL_CONTEXT | NEEDS_REVIEW |
| MF-15 | Giá trị ngoài thang | INVALID_INPUT | INVALID_INPUT | NEEDS_REVIEW |
| MF-16 | Một đường g=4 và đường chưa rõ | [12.96, 15.2] · HIGH · REVIEW | [12.9, 15.2] · HIGH · REVIEW | NEEDS_REVIEW |
| MF-17 | Bypass g=5 và một đường chưa rõ | 15 · HIGH · REVIEW | 15.0 · HIGH · REVIEW | NEEDS_REVIEW |
| MF-18 | Mọi đường đã biết, max nhỏ hơn 5 | 10.2 · HIGH | 10.2 · HIGH | EVALUATED |
| MF-19 | Đường chưa rõ có cận được xác nhận | [7.8, 10.2] · MODERATE–HIGH · REVIEW | [7.8, 10.2] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-20 | P=1, G chưa rõ, I_total=3 | 3 · LOW · REVIEW | 3.0 · LOW · REVIEW | NEEDS_REVIEW |
| MF-21 | E gợi ý từ template chưa xác nhận | [5.88, 7.8] · MODERATE · REVIEW | [5.8, 7.8] · MODERATE · REVIEW | NEEDS_REVIEW |
| MF-22 | Cận G chưa được xác nhận bị bỏ qua | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15.0] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-23 | Điểm không nguyên | INVALID_INPUT | INVALID_INPUT | NEEDS_REVIEW |
| MF-24 | Max đã xác định dưới 5 nhờ cận đường khác | 10.2 · HIGH · REVIEW | 10.2 · HIGH · REVIEW | NEEDS_REVIEW |
| MF-25 | Danh sách đường chưa đầy đủ | [7.8, 15] · MODERATE–HIGH · REVIEW | [7.8, 15.0] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-26 | Cận đầu vào sai | INVALID_BOUND_INPUT | INVALID_BOUND_INPUT | NEEDS_REVIEW |

## 2. Kết quả kiểm tra số học

**PASS:** 26 kỳ vọng cố định; 8 biên raw; 625 tổ hợp E/F/G/I_total đối chiếu công thức phân số độc lập; 2000 bước tăng một yếu tố kiểm tra đơn điệu điểm/nhãn; 50,625 hộp miền nguyên với 1,500,625 tổ hợp hoàn thiện, trong đó 675 hộp co thành điểm; 3,179 tổ hợp hoàn thiện của fixture; 182 hàng độ nhạy; 3 biến thể trọng số.

Bất biến đã kiểm tra: R ∈ [1,25]; tăng yếu tố không làm giảm R; I_total≤2 ⇒ nhãn≤MODERATE; CRITICAL ⇒ I_total≥4; G=1 ⇒ R≤9; P=1 ⇒ L=1. Cắt điểm xuống 1 chữ số thập phân giữ nguyên raw_level trên toàn bộ miền; final_level vẫn áp dụng cổng impact. Mọi hộp co thành điểm đều có I_total và final_level xác định.

MF-12 nay có score=13/HIGH; MF-13 có score=1/LOW; cả hai NEEDS_REVIEW. MF-17 có G=5/score=15/HIGH nhưng đường recovery chưa rõ. MF-16 vẫn có score=null dù level_range=[HIGH,HIGH], vì R=[12.96,15.2]. MF-24 xác định G=3 nhờ cận đường còn lại≤2; gap evidence vẫn còn. MF-25 thêm đường UNASSESSED_SCOPE=[1,5], không suy danh sách đã đầy đủ.

Hệ quả G=1⇒R≤9 được giữ như lựa chọn của profile có điều kiện, có nền dương: ngay cả I_total=5 cũng tối đa MODERATE. G=1 chỉ là tiêu chí đã xác minh trong scope/thời điểm/cấu hình được ghi; không khẳng định control hoàn hảo. Hiển thị impact=5 và vector vẫn bắt buộc; nhãn không tự chấp nhận risk hoặc đóng control gap. P=1 không chứng minh G tốt.

Kiểm tra trên xác nhận tính nhất quán của mô hình đã chọn; không chứng minh trọng số, rubric hay ngưỡng đã phản ánh rủi ro thực tế.

## 3. Độ nhạy ±1 từng yếu tố trên toàn bộ fixture

Giữ các biến khác cố định. BOUNDARY là hướng ngoài 1–5; UNKNOWN dùng hai đầu miền, không gọi là ±1 quanh một điểm giả. Case input/context lỗi ghi NOT_RUN. Với G suy từ các đường, đây là biến thể giả định của G tổng hợp để kiểm tra công thức; không sửa evidence đường và không suy đã khắc phục/control đạt từ trạng thái probe. Evidence gaps của assessment gốc vẫn theo baseline. Các đầu miền được cố định riêng chỉ phục vụ tính toán, không xác nhận UNKNOWN trong assessment thật.

### MF-01 — baseline 7.8 · MODERATE

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 7.32 · MODERATE | BOUNDARY | ±1 |
| F | 5 | 7.08 · MODERATE | BOUNDARY | ±1 |
| G | 2 | 5.4 · MODERATE | 10.2 · HIGH | ±1 |
| C | 3 | 5.2 · MODERATE | 10.4 · HIGH | ±1 |
| I_integrity | 2 | 7.8 · MODERATE | 7.8 · MODERATE | ±1 |
| A | 1 | BOUNDARY | 7.8 · MODERATE | ±1 |
| B | 2 | 7.8 · MODERATE | 7.8 · MODERATE | ±1 |

### MF-02 — baseline 15 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 13.8 · HIGH | BOUNDARY | ±1 |
| F | 5 | 13.2 · HIGH | BOUNDARY | ±1 |
| G | 5 | 12.6 · HIGH | BOUNDARY | ±1 |
| C | 3 | 10 · MODERATE | 20 · CRITICAL | ±1 |
| I_integrity | 2 | 15 · HIGH | 15 · HIGH | ±1 |
| A | 1 | BOUNDARY | 15 · HIGH | ±1 |
| B | 2 | 15 · HIGH | 15 · HIGH | ±1 |

### MF-03 — baseline 12.96 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 11.68 · HIGH | BOUNDARY | ±1 |
| F | 3 | 11.04 · HIGH | 14.88 · HIGH | ±1 |
| G | 4 | 10.72 · HIGH | 15.2 · HIGH | ±1 |
| C | 4 | 9.72 · MODERATE | 16.2 · HIGH | ±1 |
| I_integrity | 1 | BOUNDARY | 12.96 · HIGH | ±1 |
| A | 1 | BOUNDARY | 12.96 · HIGH | ±1 |
| B | 3 | 12.96 · HIGH | 12.96 · HIGH | ±1 |

### MF-04 — baseline 12.32 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 3 | 11.04 · HIGH | 13.6 · HIGH | ±1 |
| F | 4 | 10.4 · HIGH | 14.24 · HIGH | ±1 |
| G | 4 | 10.24 · HIGH | 14.4 · HIGH | ±1 |
| C | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1 |
| I_integrity | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1 |
| A | 3 | 12.32 · HIGH | 12.32 · HIGH | ±1 |
| B | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1 |

### MF-05 — baseline [1.8, 25] · LOW–CRITICAL · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [1.72, 23] · LOW–CRITICAL · REVIEW | BOUNDARY | ±1 |
| F | 5 | [1.68, 22] · LOW–CRITICAL · REVIEW | BOUNDARY | ±1 |
| G | UNKNOWN | [1.8, 9] · LOW–MODERATE · REVIEW | [5, 25] · LOW–CRITICAL · REVIEW | Hai đầu miền UNKNOWN |
| C | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | Hai đầu miền UNKNOWN |
| I_integrity | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | Hai đầu miền UNKNOWN |
| A | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | Hai đầu miền UNKNOWN |
| B | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | Hai đầu miền UNKNOWN |

### MF-06 — baseline 1 · LOW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 1 | BOUNDARY | 1.08 · LOW | ±1 |
| F | 1 | BOUNDARY | 1.12 · LOW | ±1 |
| G | 1 | BOUNDARY | 1 · LOW | ±1 |
| C | 1 | BOUNDARY | 2 · LOW | ±1 |
| I_integrity | 1 | BOUNDARY | 2 · LOW | ±1 |
| A | 1 | BOUNDARY | 2 · LOW | ±1 |
| B | 1 | BOUNDARY | 2 · LOW | ±1 |

### MF-07 — baseline 25 · CRITICAL

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 23 · CRITICAL | BOUNDARY | ±1 |
| F | 5 | 22 · CRITICAL | BOUNDARY | ±1 |
| G | 5 | 21 · CRITICAL | BOUNDARY | ±1 |
| C | 5 | 25 · CRITICAL | BOUNDARY | ±1 |
| I_integrity | 5 | 25 · CRITICAL | BOUNDARY | ±1 |
| A | 5 | 25 · CRITICAL | BOUNDARY | ±1 |
| B | 5 | 25 · CRITICAL | BOUNDARY | ±1 |

### MF-08 — baseline 5 · LOW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 4.6 · LOW | BOUNDARY | ±1 |
| F | 5 | 4.4 · LOW | BOUNDARY | ±1 |
| G | 5 | 4.2 · LOW | BOUNDARY | ±1 |
| C | 1 | BOUNDARY | 10 · MODERATE | ±1 |
| I_integrity | 1 | BOUNDARY | 10 · MODERATE | ±1 |
| A | 1 | BOUNDARY | 10 · MODERATE | ±1 |
| B | 1 | BOUNDARY | 10 · MODERATE | ±1 |

### MF-09 — baseline 10 · MODERATE

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 9.2 · MODERATE | BOUNDARY | ±1 |
| F | 5 | 8.8 · MODERATE | BOUNDARY | ±1 |
| G | 5 | 8.4 · MODERATE | BOUNDARY | ±1 |
| C | 2 | 10 · MODERATE | 15 · HIGH | ±1 |
| I_integrity | 2 | 10 · MODERATE | 15 · HIGH | ±1 |
| A | 2 | 10 · MODERATE | 15 · HIGH | ±1 |
| B | 2 | 10 · MODERATE | 15 · HIGH | ±1 |

### MF-10 — baseline [5.4, 15] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [5.16, 13.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | [5.04, 13.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| G | UNKNOWN | 5.4 · MODERATE · REVIEW | 15 · HIGH · REVIEW | Hai đầu miền UNKNOWN |
| C | 3 | [3.6, 10] · LOW–MODERATE · REVIEW | [7.2, 20] · MODERATE–CRITICAL · REVIEW | ±1 |
| I_integrity | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |
| B | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |

### MF-11 — baseline [7.8, 13] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [7.32, 12.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | [7.08, 11.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| G | 2 | [5.4, 9] · MODERATE · REVIEW | [10.2, 17] · HIGH–CRITICAL · REVIEW | ±1 |
| C | 3 | [5.2, 13] · MODERATE–HIGH · REVIEW | [10.4, 13] · HIGH · REVIEW | ±1 |
| I_integrity | UNKNOWN | 7.8 · MODERATE · REVIEW | 13 · HIGH · REVIEW | Hai đầu miền UNKNOWN |
| A | 1 | BOUNDARY | [7.8, 13] · MODERATE–HIGH · REVIEW | ±1 |
| B | 2 | [7.8, 13] · MODERATE–HIGH · REVIEW | [7.8, 13] · MODERATE–HIGH · REVIEW | ±1 |

### MF-12 — baseline 13 · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 12.2 · HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | 11.8 · HIGH · REVIEW | BOUNDARY | ±1 |
| G | 2 | 9 · MODERATE · REVIEW | 17 · CRITICAL · REVIEW | ±1 |
| C | 5 | [10.4, 13] · HIGH · REVIEW | BOUNDARY | ±1 |
| I_integrity | UNKNOWN | 13 · HIGH · REVIEW | 13 · HIGH · REVIEW | Hai đầu miền UNKNOWN |
| A | 1 | BOUNDARY | 13 · HIGH · REVIEW | ±1 |
| B | 2 | 13 · HIGH · REVIEW | 13 · HIGH · REVIEW | ±1 |

### MF-13 — baseline 1 · LOW · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 1 | BOUNDARY | [1.08, 1.4] · LOW · REVIEW | ±1 |
| F | 1 | BOUNDARY | [1.12, 1.6] · LOW · REVIEW | ±1 |
| G | UNKNOWN | 1 · LOW · REVIEW | 1 · LOW · REVIEW | Hai đầu miền UNKNOWN |
| C | 1 | BOUNDARY | 2 · LOW · REVIEW | ±1 |
| I_integrity | 1 | BOUNDARY | 2 · LOW · REVIEW | ±1 |
| A | 1 | BOUNDARY | 2 · LOW · REVIEW | ±1 |
| B | 1 | BOUNDARY | 2 · LOW · REVIEW | ±1 |

### MF-14 — baseline MISSING_ESSENTIAL_CONTEXT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| G | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |

### MF-15 — baseline INVALID_INPUT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 0 | NOT_RUN | NOT_RUN | Context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| G | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |

### MF-16 — baseline [12.96, 15.2] · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [11.68, 13.6] · HIGH · REVIEW | BOUNDARY | ±1 |
| F | 3 | [11.04, 12.8] · HIGH · REVIEW | [14.88, 17.6] · HIGH–CRITICAL · REVIEW | ±1 |
| G | UNKNOWN | 12.96 · HIGH · REVIEW | 15.2 · HIGH · REVIEW | Hai đầu miền UNKNOWN; giả định G tổng hợp |
| C | 4 | [9.72, 11.4] · MODERATE–HIGH · REVIEW | [16.2, 19] · HIGH–CRITICAL · REVIEW | ±1 |
| I_integrity | 1 | BOUNDARY | [12.96, 15.2] · HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | [12.96, 15.2] · HIGH · REVIEW | ±1 |
| B | 3 | [12.96, 15.2] · HIGH · REVIEW | [12.96, 15.2] · HIGH · REVIEW | ±1 |

### MF-17 — baseline 15 · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 13.8 · HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | 13.2 · HIGH · REVIEW | BOUNDARY | ±1 |
| G | 5 | 12.6 · HIGH · REVIEW | BOUNDARY | ±1; giả định G tổng hợp |
| C | 3 | 10 · MODERATE · REVIEW | 20 · CRITICAL · REVIEW | ±1 |
| I_integrity | 2 | 15 · HIGH · REVIEW | 15 · HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | 15 · HIGH · REVIEW | ±1 |
| B | 2 | 15 · HIGH · REVIEW | 15 · HIGH · REVIEW | ±1 |

### MF-18 — baseline 10.2 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 9.48 · MODERATE | BOUNDARY | ±1 |
| F | 5 | 9.12 · MODERATE | BOUNDARY | ±1 |
| G | 3 | 7.8 · MODERATE | 12.6 · HIGH | ±1; giả định G tổng hợp |
| C | 3 | 6.8 · MODERATE | 13.6 · HIGH | ±1 |
| I_integrity | 2 | 10.2 · HIGH | 10.2 · HIGH | ±1 |
| A | 1 | BOUNDARY | 10.2 · HIGH | ±1 |
| B | 2 | 10.2 · HIGH | 10.2 · HIGH | ±1 |

### MF-19 — baseline [7.8, 10.2] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [7.32, 9.48] · MODERATE · REVIEW | BOUNDARY | ±1 |
| F | 5 | [7.08, 9.12] · MODERATE · REVIEW | BOUNDARY | ±1 |
| G | UNKNOWN | 7.8 · MODERATE · REVIEW | 10.2 · HIGH · REVIEW | Hai đầu miền UNKNOWN; giả định G tổng hợp |
| C | 3 | [5.2, 6.8] · MODERATE · REVIEW | [10.4, 13.6] · HIGH · REVIEW | ±1 |
| I_integrity | 2 | [7.8, 10.2] · MODERATE–HIGH · REVIEW | [7.8, 10.2] · MODERATE–HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | [7.8, 10.2] · MODERATE–HIGH · REVIEW | ±1 |
| B | 2 | [7.8, 10.2] · MODERATE–HIGH · REVIEW | [7.8, 10.2] · MODERATE–HIGH · REVIEW | ±1 |

### MF-20 — baseline 3 · LOW · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 1 | BOUNDARY | [3.24, 4.2] · LOW · REVIEW | ±1 |
| F | 1 | BOUNDARY | [3.36, 4.8] · LOW · REVIEW | ±1 |
| G | UNKNOWN | 3 · LOW · REVIEW | 3 · LOW · REVIEW | Hai đầu miền UNKNOWN |
| C | 3 | 2 · LOW · REVIEW | 4 · LOW · REVIEW | ±1 |
| I_integrity | 2 | 3 · LOW · REVIEW | 3 · LOW · REVIEW | ±1 |
| A | 1 | BOUNDARY | 3 · LOW · REVIEW | ±1 |
| B | 2 | 3 · LOW · REVIEW | 3 · LOW · REVIEW | ±1 |

### MF-21 — baseline [5.88, 7.8] · MODERATE · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | UNKNOWN | 5.88 · MODERATE · REVIEW | 7.8 · MODERATE · REVIEW | Hai đầu miền UNKNOWN |
| F | 5 | [5.16, 7.08] · MODERATE · REVIEW | BOUNDARY | ±1 |
| G | 2 | [4.44, 5.4] · LOW–MODERATE · REVIEW | [7.32, 10.2] · MODERATE–HIGH · REVIEW | ±1 |
| C | 3 | [3.92, 5.2] · LOW–MODERATE · REVIEW | [7.84, 10.4] · MODERATE–HIGH · REVIEW | ±1 |
| I_integrity | 2 | [5.88, 7.8] · MODERATE · REVIEW | [5.88, 7.8] · MODERATE · REVIEW | ±1 |
| A | 1 | BOUNDARY | [5.88, 7.8] · MODERATE · REVIEW | ±1 |
| B | 2 | [5.88, 7.8] · MODERATE · REVIEW | [5.88, 7.8] · MODERATE · REVIEW | ±1 |

### MF-22 — baseline [5.4, 15] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [5.16, 13.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | [5.04, 13.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| G | UNKNOWN | 5.4 · MODERATE · REVIEW | 15 · HIGH · REVIEW | Hai đầu miền UNKNOWN |
| C | 3 | [3.6, 10] · LOW–MODERATE · REVIEW | [7.2, 20] · MODERATE–CRITICAL · REVIEW | ±1 |
| I_integrity | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |
| B | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1 |

### MF-23 — baseline INVALID_INPUT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 2.5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| G | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |

### MF-24 — baseline 10.2 · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 9.48 · MODERATE · REVIEW | BOUNDARY | ±1 |
| F | 5 | 9.12 · MODERATE · REVIEW | BOUNDARY | ±1 |
| G | 3 | 7.8 · MODERATE · REVIEW | 12.6 · HIGH · REVIEW | ±1; giả định G tổng hợp |
| C | 3 | 6.8 · MODERATE · REVIEW | 13.6 · HIGH · REVIEW | ±1 |
| I_integrity | 2 | 10.2 · HIGH · REVIEW | 10.2 · HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | 10.2 · HIGH · REVIEW | ±1 |
| B | 2 | 10.2 · HIGH · REVIEW | 10.2 · HIGH · REVIEW | ±1 |

### MF-25 — baseline [7.8, 15] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [7.32, 13.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| F | 5 | [7.08, 13.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1 |
| G | UNKNOWN | 7.8 · MODERATE · REVIEW | 15 · HIGH · REVIEW | Hai đầu miền UNKNOWN; giả định G tổng hợp |
| C | 3 | [5.2, 10] · MODERATE · REVIEW | [10.4, 20] · HIGH–CRITICAL · REVIEW | ±1 |
| I_integrity | 2 | [7.8, 15] · MODERATE–HIGH · REVIEW | [7.8, 15] · MODERATE–HIGH · REVIEW | ±1 |
| A | 1 | BOUNDARY | [7.8, 15] · MODERATE–HIGH · REVIEW | ±1 |
| B | 2 | [7.8, 15] · MODERATE–HIGH · REVIEW | [7.8, 15] · MODERATE–HIGH · REVIEW | ±1 |

### MF-26 — baseline INVALID_BOUND_INPUT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Context/input lỗi |
| G | UNKNOWN | NOT_RUN | NOT_RUN | Context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Context/input lỗi |

## 4. Độ nhạy trọng số và review cặp MF-03/MF-04

MF-03: G±1 đổi R ±2.24; F±1 đổi ±1.92; E−1 đổi −1.28, E+1 ngoài biên. C±1 đổi ±3.24; I_integrity/A/B không đổi max ở các hướng hợp lệ. C giảm 4→3 cho R=9.72, hiển thị 9.7 MODERATE. Khi thay trọng số, phải tính cả hai ca:

| Trọng số E/F | R MF-03 | R MF-04 | Quan hệ số học |
| --- | --- | --- | --- |
| 0.3/0.7 | 12.32 | 12.64 | MF-03 < MF-04 |
| 0.4/0.6 — profile hiện hành | 12.96 | 12.32 | MF-03 > MF-04 |
| 0.5/0.5 | 13.60 | 12.00 | MF-03 > MF-04 |

Với trọng số E là w, R03=10.4+6.4w và R04=13.6−3.2w; giao nhau tại w=1/3. Hai biến thể 30/70 và 50/50 là sensitivity ngoài profile, không ghi vào assessment như kết quả của 40/60. Nếu đổi trọng số áp dụng cần version mới; không dùng công thức R25 của 40/60 cho trọng số khác. Ba cặp/6 phép tính này nằm trong fixture bổ sung và script kiểm tra.

| Nội dung | MF-03 | MF-04 |
| --- | --- | --- |
| E/F/G | 5/3/4 | 3/4/4 |
| C/I_integrity/A/B | 4/1/1/3 | 4/4/3/4 |
| R chính xác | 12.96 | 12.32 |
| Hiển thị | 12.9 HIGH | 12.3 HIGH |
| Độ khả dĩ tiền điều kiện thực tế | UNKNOWN | UNKNOWN |

### Quyết định review hiện hành — r2 ngày 2026-10-11; làm rõ thẩm quyền ở r3 ngày 2026-10-12

**Người review: trợ lý Codex (AI). `decision_type=REVIEWER_DETERMINATION`; `priority_decision=NOT_RANKED`; `review_status=COMPLETED_WITH_LIMITATIONS`.** Ghi nhận lại lúc `2026-10-12T15:27:29+07:00` (Asia/Bangkok); quyết định gốc ngày 2026-10-11. `user_confirmation=NOT_RECORDED`. Giữ hai ca cùng nhãn HIGH theo profile, không gán MF-03 hoặc MF-04 ưu tiên trước với dữ liệu hiện có. Lý do: tiền điều kiện thực tế chưa có căn cứ; thứ tự R đảo khi đổi trọng số chưa hiệu chuẩn; max không thể hiện độ rộng hậu quả. E/F cũng khác nhau, nên MF-04 không trội hơn trên toàn bộ đầu vào dù vector impact không thấp hơn.

Đây là kết luận review của trợ lý cho hai ca giả lập, không phải phê duyệt của người dùng/SME; bản thân quyết định này không đóng bước 02. Việc đóng băng thiết kế được ghi riêng tại kế hoạch mục 19. Các quyết định ưu tiên thực tế có thể được người có quyền đưa ra khi có context/evidence và lý do, nhưng không được suy chỉ từ R. Không bắt người dùng tự chấm lại các phép tính.

**Dòng dành cho người dùng:** ☐ Xác nhận giữ NOT_RANKED · ☐ Đổi thành ______; lý do ______; người xác nhận ______; thời điểm ______. **Hiện chưa có xác nhận/đổi được ghi nhận; không tự điền thay người dùng.** Dòng này áp dụng quyết định ưu tiên của cặp minh họa, không phải yêu cầu chấm lại fixture hay điều kiện còn mở của thiết kế bước 02.

**Lịch sử đính chính:** đề xuất trước đây của trợ lý “MF-04 trước khi tiền điều kiện tương đương và ưu tiên hậu quả rộng” chỉ là ý kiến có điều kiện. Bản r2 thay thế đề xuất đó bằng quyết định NOT_RANKED cho dữ liệu đang có; gỡ nhận xét khỏi phương pháp và README hiện hành. Không thay đổi fixture/điểm để ép một thứ tự ưu tiên.

### 4.1. Tiến độ impact dù R không đổi

Giữ E/F/G=3/4/4, L=3.08 và context so sánh. Các ví dụ dưới giả định căn cứ trước/sau đã được xác nhận trong bài tính tổng hợp:

| Trước → sau (C/I_integrity/A/B) | Chiều giảm | I_total sau | R sau | impact_progress |
| --- | --- | --- | --- | --- |
| (4,4,3,4) → (3,4,3,4) | C | 4 | 12.32 HIGH | IMPROVED |
| (4,4,3,4) → (4,3,3,4) | I_integrity | 4 | 12.32 HIGH | IMPROVED |
| (4,4,3,4) → (4,4,3,3) | B | 4 | 12.32 HIGH | IMPROVED |
| (4,4,3,4) → (3,3,3,4) | C, I_integrity | 4 | 12.32 HIGH | IMPROVED |
| (4,4,3,4) → (3,3,3,3) | C, I_integrity, B | 3 | 9.24 MODERATE | IMPROVED |

Retest hai chiều đã giảm phải báo “C và Integrity đã cải thiện; R chưa đổi vì B vẫn ở mức 4”. Đây không phải tỷ lệ giảm tổn thất hoặc tự đóng treatment. Fixture bổ sung còn kiểm tra MIXED, WORSENED, UNCHANGED, INCOMPLETE, context/loại assessment khác, UNKNOWN được làm rõ, evidence chưa xác minh và liên hệ treatment chưa đủ.

## 5. Hai người chấm G và việc còn thiếu

Phiếu A và phiếu B dùng cùng 6 case tổng hợp. **NOT_RUN**: chưa có người chấm hoặc số liệu đồng thuận; kiểm tra tính toán và tác giả tự chấm không thay thế hai người độc lập. GR-06 phải giữ gap recovery dù G=5 đã xác định.

Khi có kết quả: báo số ca cả hai có số, số ca UNKNOWN, tỷ lệ trùng G với mẫu số rõ, phân phối |G_A−G_B|, lệch≥2, xung đột coverage và thay đổi nhãn. Phân xử có rationale và giữ bản gốc; không tự lấy trung bình G hoặc tuyên bố độ tin cậy thống kê từ mẫu nhỏ.

Quyết định review cặp MF-03/MF-04 ở mục 4 là NOT_RANKED với dữ liệu hiện có. Thiết kế bước 02 đã được đóng băng ở r3 theo kế hoạch mục 19. Kiểm tra hai người chấm được chuyển thành VALID-G-01 tại bước 06: NOT_RUN, độ tin cậy giữa người chấm của rubric G chưa được kiểm chứng. Evidence thực tế và hiệu chuẩn SME vẫn chưa có và không được suy từ fixture. Control/evidence và test case tiếp tục là thiết kế; bước 03–06 NOT_STARTED, chưa chạy lab.

## 6. Đính chính và tái lập

**Lần kiểm tra tái lập ngày 2026-10-12: PASS.** Các số đếm gốc ở mục 2 được tính lại và khớp với fixture đã lưu, gồm 229 probe độ nhạy hợp lệ trong 182 hàng. Bổ sung: 20 ca impact_progress (16 ca r2 và 4 ca mới), 3 cặp trọng số (6 phép tính), 2 ca hiển thị và 1 ca bất đồng. Trong 675 hộp co điểm, 50 hộp còn G chưa xác định, tất cả E=F=1. Cổng impact đổi nhãn đúng hai bộ (5,5,5,1) và (5,5,5,2). Kết quả và hash đầu vào/script được lưu trong verification-results-v0.4.json.

Fixture số học chính giữ nguyên các kỳ vọng; script độc lập đọc JSON và đối chiếu lại, không tạo lại expected trước khi kiểm tra. Hướng dẫn chỉ rõ các file cần có, lệnh chạy và phạm vi các số đếm. Kết quả lần chạy được lưu ở [verification-results-v0.4.json](../Dac-ta-ky-thuat/verification-results-v0.4.json); không yêu cầu môi trường CRM, mạng hoặc thư viện ngoài Python chuẩn.

Các bổ sung được kiểm tra riêng: hai tổ hợp chịu tác động cổng impact; mọi hộp co thành điểm đều có E/F/I_total xác định; bảng trọng số cho cả hai ca; các tình huống impact_progress; nhãn từ cận chính xác. Ca hiển thị hợp lệ E=1,F=2,G=2,I_total∈[3,4] cho [3.72,4.96] → [3.7,5.0] LOW–LOW. Điểm 9.96 dùng riêng để kiểm tra hàm định dạng, không thuộc tập điểm có thể sinh của profile v0.4. Điểm lớn nhất dưới 10 của profile là 9.8.

Khôi phục các quy tắc v0.2 bị thiếu: cùng CURRENT/INHERENT; không cộng scenario/tactic; ATT&CK chỉ metadata; confidence không nhân R; bất đồng chưa giải quyết giữ NEEDS_REVIEW. Việc thiếu trước đây là lỗi biên tập. NIST được kiểm tra trực quan lại ngày 2026-10-12: Table G-2/G-3/G-4/G-5 cùng trang in G-2 (PDF 82); PDF 83 đã sang H-1. Số trang r2 đúng với bản final đang dẫn; không cần bỏ số trang hoặc ghi chưa đối chiếu. Phạm vi nguồn và liên kết xem phương pháp mục 8.

## 7. Bổ sung r3 và đối chiếu sáu nhận xét — 2026-10-12

1. **NIST:** giữ số trang r2 sau khi tải lại PDF chính thức và xem trực quan PDF 81–86, 42–43. PDF 81=G-1 (Table G-1), 82=G-2 (Tables G-2…G-5), 83–85=H-1…H-3, 86=I-1. Task 2-4 ở trang in 33–34/PDF 42–43. SHA-256 nguồn PDF: `f214087f0bdb35932a28c16eb93932a33c67a6edfb5e6f1638866bd201c98e04`. Table G-4 là likelihood có hậu quả, không là impact severity. [Nguồn chính thức, trang 82](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf#page=82).
2. **Quy tắc từ v0.2:** khôi phục nhãn độc lập để kiểm chứng AI; bộ tính theo version quyết định phép tính, người xác minh đầu vào. Fixture NOT_IMPLEMENTED/ENROLLED_SIMULATED không chứng minh môi trường thật có hay không có control.
3. **Kế hoạch:** sửa chat bước 02, phân biệt chỉ mục dự án với planning, gắn SUPERSEDED ngay tiểu mục quyết định cũ; trạng thái hiện hành ở mục 19.
4. **Lab fixture:** tiêu chí enrollment/recovery DEFINED_IN_CE-01_v0.1, tham chiếu C04/C05; thresholds TO_SET_BEFORE_LAB, implementation_status vẫn NOT_IMPLEMENTED.
5. **Theo dõi impact:** thêm cờ verified_worsening cùng summary max trước/sau và số chiều bằng max. Chỉ bổ sung trường mô tả/cảnh báo; IMPACT-PROGRESS-v0.1 và các nhãn tổng hợp/điểm cũ không đổi. Fixture bổ sung ghi revision v0.1-r2 để phân biệt với bundle trước.
6. **Thẩm quyền:** NOT_RANKED là REVIEWER_DETERMINATION của trợ lý; có thời điểm/lý do và dòng riêng cho người dùng xác nhận/đổi, hiện NOT_RECORDED. Không giả ghi người dùng đã phê duyệt.

### Các trường mới và ca hồi quy

| Ca | Kết quả cần bảo toàn |
| --- | --- |
| IP-01 / IP-04 | I_total 4→4; số chiều bằng max 3→2 / 3→1; R giữ 12.32 nhưng impact IMPROVED, verified_worsening=false |
| IP-05 | I_total 4→3, số chiều bằng max 3→4; số đếm tăng không được diễn giải là xấu đi |
| IP-17 | Có chiều UP đã xác minh cùng chiều UNKNOWN: INCOMPLETE nhưng verified_worsening=true; max có thể xác định 5 còn số chiều bằng max chưa xác định |
| IP-18 | Snapshot trước max=5 có chiều UNKNOWN: I_total xác định nhưng số chiều bằng max∈[1,2]; bổ sung evidence sau không chứng minh chiều đó giảm/giữ nguyên, verified_worsening=null |
| IP-19 | Context khác: summary mỗi bên vẫn mô tả được, verified_worsening=null; không suy tiến độ từ chênh lệch |
| IP-20 | Điểm C=5 chỉ là đề xuất chưa xác minh: không bão hòa max, không gắn cờ xấu đi; giữ UNKNOWN và range |

**Kết quả:** 20 ca impact được đối chiếu bằng verifier, giữ nguyên input và các kỳ vọng cũ của 16 ca r2; fixture số học chính giữ nguyên byte. Kết quả và hash mới ở verification-results-v0.4.json. PASS chỉ áp dụng cho các quy tắc được kiểm tra, không là bằng chứng đồng thuận người chấm hoặc hiệu lực CRM.

**Bàn giao:** đóng băng thiết kế bước 02; VALID-G-01, bước 06, NOT_RUN. Trạng thái chấm G vẫn chưa kiểm chứng, phiếu A/B vẫn trống. Snapshot r2 có đủ bộ tái lập trong gói lịch sử.
