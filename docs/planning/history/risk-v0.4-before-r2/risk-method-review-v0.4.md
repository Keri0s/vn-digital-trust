# Review và kiểm tra RM-01 v0.4

**Ngày:** 2026-10-10. **Cập nhật review:** 2026-10-11. **Trạng thái:** DRAFT_REVIEW; bước 02 IN_PROGRESS.

Nguồn quy tắc: [RM-01 v0.4](risk-method-v0.4.md); [fixture JSON](../../verification/risk-method-fixtures-v0.4.json). Đây là kiểm tra phép tính thiết kế. Mọi trạng thái evidence/xác nhận trong fixture là giả định tổng hợp; không có kết quả CRM/lab, hiệu chuẩn SME hoặc người chấm độc lập. EVALUATED trong bảng chỉ là trạng thái mà đầu vào giả định đầy đủ sẽ cho ra.

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

## 4. Độ nhạy trọng số và giới hạn max impact

MF-03: G±1 đổi R ±2.24; F±1 đổi ±1.92; E−1 đổi −1.28, E+1 ngoài biên. C±1 đổi ±3.24; I_integrity/A/B chưa đổi max ở các hướng hợp lệ. C giảm 4→3 cho R=9.72, hiển thị 9.7 · MODERATE. E/F đổi 10 điểm phần trăm chỉ làm R đổi ±0.64:

| Trọng số E/F | R MF-03 | Chênh lệch |
| --- | --- | --- |
| 0.3/0.7 | 12.32 | -0.64 |
| 0.4/0.6 | 12.96 | 0 |
| 0.5/0.5 | 13.6 | 0.64 |

Biến thể trọng số là phân tích độ nhạy ngoài profile đang lưu. Nếu áp dụng trọng số mới cho assessment, phải tạo version mới; không dùng R25 của 40/60 cho công thức đã đổi.

| Nội dung | MF-03 | MF-04 |
| --- | --- | --- |
| E/F/G | 5/3/4 | 3/4/4 |
| C/I_integrity/A/B | 4/1/1/3 | 4/4/3/4 |
| R chính xác | 12.96 | 12.32 |
| Hiển thị | 12.9 · HIGH | 12.3 · HIGH |
| Số chiều impact bằng 4 | 1 | 3 |
| Độ khả dĩ tiền điều kiện thực tế | UNKNOWN | UNKNOWN |

### Kết luận review thiết kế — 2026-10-11

**Trạng thái: DESIGN_REVIEW_COMPLETED. Người review: trợ lý Codex, theo yêu cầu người dùng.** Đây là nhận xét cho hai ca tổng hợp, không phải phê duyệt/chấp nhận rủi ro của SME hoặc kết quả người chấm G độc lập. Người dùng không cần tự tính hoặc chấm lại MF-03/MF-04.

- **Điểm giữ nguyên:** MF-03 = 12.96 HIGH; MF-04 = 12.32 HIGH. Cả hai cùng nhóm xử lý HIGH. Chênh lệch 0.64 không tự quyết định thứ tự xử lý.
- **Đề xuất có điều kiện:** nếu cần thứ tự minh họa, MF-04 trước MF-03, với giả định độ khả dĩ tiền điều kiện tương đương và reviewer chọn ưu tiên hậu quả rộng hơn trong cùng nhóm HIGH. MF-04 có C=4 như MF-03, nhưng Integrity 4 thay vì 1, Availability 3 thay vì 1 và B 4 thay vì 3. Mọi chiều hậu quả đều không thấp hơn; Integrity và nghiệp vụ cùng đạt mức 4 bên cạnh Confidentiality.
- **Đánh đổi được ghi rõ:** MF-03 có P=3.8/L=3.24, MF-04 có P=3.6/L=3.08. Vì E/F khác nhau, MF-04 không trội hơn trên toàn bộ đầu vào. Đề xuất ưu tiên là nhận xét của reviewer khi coi trọng hậu quả rộng, không phải thứ tự tất yếu từ công thức hoặc quy tắc xếp hạng tự động mới.
- **Độ nhạy:** 0.64 nhỏ hơn thay đổi R khi G lệch một mức ở MF-03 (2.24) hoặc C lệch một mức (3.24). Điều này cho thấy cần cân nhắc sai khác khi chấm; không chứng minh hai rủi ro tương đương về thống kê hay cho phép bỏ qua chênh lệch bất kỳ.
- **Giới hạn áp dụng:** precondition_plausibility thực tế của cả hai vẫn UNKNOWN. Vì vậy ưu tiên xử lý thực tế là NOT_DETERMINED; không điền giả nhãn độ khả dĩ bằng nhau. Evidence cho thấy tiền điều kiện MF-03 dễ đạt hơn đáng kể hoặc mục tiêu xử lý khác có thể thay đổi đề xuất.

**Kết luận đối với phương pháp:** giữ max impact cho chỉ số tổng hợp và hiển thị vector đầy đủ để reviewer cân nhắc độ rộng hậu quả. Cặp này minh họa rõ giới hạn của max; không sửa điểm/hệ số để ép MF-04 có R cao hơn. Kết quả review thiết kế đã hoàn tất; thu dữ liệu doanh nghiệp thực tế là công việc đánh giá sau này, không phải yêu cầu người dùng đoán câu trả lời cho fixture.

## 5. Hai người chấm G và việc còn thiếu

[Phiếu A](../../review-forms/risk-g-rating-a-v0.4.md) và [phiếu B](../../review-forms/risk-g-rating-b-v0.4.md) dùng cùng 6 case tổng hợp. **NOT_RUN**: chưa có người chấm hoặc số liệu đồng thuận; kiểm tra tính toán và tác giả tự chấm không thay thế hai người độc lập. GR-06 phải giữ gap recovery dù G=5 đã xác định.

Khi có kết quả: báo số ca cả hai có số, số ca UNKNOWN, tỷ lệ trùng G với mẫu số rõ, phân phối |G_A−G_B|, lệch≥2, xung đột coverage và thay đổi nhãn. Phân xử có rationale và giữ bản gốc; không tự lấy trung bình G hoặc tuyên bố độ tin cậy thống kê từ mẫu nhỏ.

Review thiết kế MF-03/MF-04 đã hoàn tất với đề xuất có điều kiện ở mục 4. Phần còn chờ để đóng review bước 02 là chấm G độc lập hoặc quyết định phạm vi kiểm tra này. Evidence thực tế và hiệu chuẩn SME vẫn chưa có và không được suy từ fixture. Control/evidence và test case tiếp tục là thiết kế. Bước 02 IN_PROGRESS; chưa chuyển bước 03 hoặc chạy lab.
