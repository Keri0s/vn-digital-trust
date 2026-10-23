# Review và kiểm tra RM-01 v0.3

**Ngày:** 2026-10-10. **Loại kiểm tra:** phép tính thiết kế, không chạy CRM/lab, không đo accuracy hay hiệu lực bảo mật.

Nguồn quy tắc: [RM-01 v0.3](risk-method-v0.3.md); [fixture JSON](risk-method-fixtures-v0.3.json). Số thập phân trong báo cáo kỹ thuật này phục vụ đối chiếu phép tính; cách hiển thị người dùng dùng số nguyên xấp xỉ.

## 1. Kết quả và các cổng mới

| Ca | Nội dung | R hoặc range chính xác · nhãn | Trạng thái |
| --- | --- | --- | --- |
| MF-01 | SC-01: control hiệu lực giả định | 7.8 · MODERATE | EVALUATED |
| MF-02 | SC-01: bypass giả định | 15 · HIGH | EVALUATED |
| MF-03 | SC-02: đường chuyển giả định | 12.96 · HIGH | EVALUATED |
| MF-04 | Đặc quyền: kiểm tra biểu diễn | 12.32 · HIGH | EVALUATED |
| MF-05 | SC-01 chưa có evidence G/impact | [1.8, 25] · LOW–CRITICAL · REVIEW | NEEDS_REVIEW |
| MF-06 | Cận dưới toàn bộ yếu tố | 1 · LOW | EVALUATED |
| MF-07 | Cận trên toàn bộ yếu tố | 25 · CRITICAL | EVALUATED |
| MF-08 | Impact gate I_total=1 | 5 · LOW | EVALUATED |
| MF-09 | Impact gate I_total=2 | 10 · MODERATE | EVALUATED |
| MF-10 | Chỉ G chưa rõ | [5.4, 15] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-11 | I_integrity chưa rõ, impact chưa xác định | [7.8, 13] · MODERATE–HIGH · REVIEW | NEEDS_REVIEW |
| MF-12 | C=5 hấp thụ I_integrity chưa rõ | 13 · HIGH · REVIEW | NEEDS_REVIEW |
| MF-13 | G chưa rõ dù range co lại | [1, 1] · LOW · REVIEW | NEEDS_REVIEW |
| MF-14 | Thiếu owner/context thiết yếu | MISSING_ESSENTIAL_CONTEXT | NEEDS_REVIEW |
| MF-15 | Giá trị ngoài thang | INVALID_INPUT | NEEDS_REVIEW |
| MF-16 | Một đường g=4 và đường chưa rõ | [12.96, 15.2] · HIGH · REVIEW | NEEDS_REVIEW |

Đã đối chiếu 16 kỳ vọng cố định, 8 biên phân mức raw, 625 tổ hợp E/F/G/I_total về cổng impact và tính đơn điệu của nhãn theo I_total; duyệt 3155 tổ hợp hoàn thiện hợp lệ để đối chiếu cận số/cận nhãn trong fixture. Ca thiếu context/ngoài thang không tính range. Kết quả: đạt các kiểm tra nêu trên. Phạm vi kiểm tra không chứng minh các trọng số/rubric đúng với SME.

MF-08: raw MODERATE → LOW do I_total=1; MF-09: raw HIGH → MODERATE do I_total=2. MF-12 có score xác định nhưng vẫn NEEDS_REVIEW vì I_integrity chưa rõ. MF-13 có range co lại nhưng không điền score khi G chưa rõ.

## 2. Độ nhạy ±1 từng yếu tố, toàn bộ fixture

Bảng dưới giữ các biến khác cố định. BOUNDARY: hướng ra ngoài 1–5; UNKNOWN: hai cột là đầu thấp/cao của miền, không phải ±1; case context/input lỗi không được tính. Với baseline còn thiếu, kết quả là range, không thay UNKNOWN bằng một điểm. Hạng risk đã qua cổng impact. Dấu REVIEW giữ trạng thái chưa đủ dữ liệu.

### MF-01 — baseline 7.8 · MODERATE

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 7.32 · MODERATE | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 7.08 · MODERATE | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 2 | 5.4 · MODERATE | 10.2 · HIGH | ±1, các yếu tố khác giữ nguyên |
| C | 3 | 5.2 · MODERATE | 10.4 · HIGH | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 2 | 7.8 · MODERATE | 7.8 · MODERATE | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | 7.8 · MODERATE | ±1, các yếu tố khác giữ nguyên |
| B | 2 | 7.8 · MODERATE | 7.8 · MODERATE | ±1, các yếu tố khác giữ nguyên |

### MF-02 — baseline 15 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 13.8 · HIGH | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 13.2 · HIGH | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 5 | 12.6 · HIGH | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| C | 3 | 10 · MODERATE | 20 · CRITICAL | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 2 | 15 · HIGH | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |
| B | 2 | 15 · HIGH | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |

### MF-03 — baseline 12.96 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 11.68 · HIGH | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 3 | 11.04 · HIGH | 14.88 · HIGH | ±1, các yếu tố khác giữ nguyên |
| G | 4 | 10.72 · HIGH | 15.2 · HIGH | ±1, các yếu tố khác giữ nguyên |
| C | 4 | 9.72 · MODERATE | 16.2 · HIGH | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 1 | BOUNDARY | 12.96 · HIGH | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | 12.96 · HIGH | ±1, các yếu tố khác giữ nguyên |
| B | 3 | 12.96 · HIGH | 12.96 · HIGH | ±1, các yếu tố khác giữ nguyên |

### MF-04 — baseline 12.32 · HIGH

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 3 | 11.04 · HIGH | 13.6 · HIGH | ±1, các yếu tố khác giữ nguyên |
| F | 4 | 10.4 · HIGH | 14.24 · HIGH | ±1, các yếu tố khác giữ nguyên |
| G | 4 | 10.24 · HIGH | 14.4 · HIGH | ±1, các yếu tố khác giữ nguyên |
| C | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1, các yếu tố khác giữ nguyên |
| A | 3 | 12.32 · HIGH | 12.32 · HIGH | ±1, các yếu tố khác giữ nguyên |
| B | 4 | 12.32 · HIGH | 15.4 · HIGH | ±1, các yếu tố khác giữ nguyên |

### MF-05 — baseline [1.8, 25] · LOW–CRITICAL · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [1.72, 23] · LOW–CRITICAL · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | [1.68, 22] · LOW–CRITICAL · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | UNKNOWN | [1.8, 9] · LOW–MODERATE · REVIEW | [5, 25] · LOW–CRITICAL · REVIEW | UNKNOWN: đầu miền 1/5 |
| C | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | UNKNOWN: đầu miền 1/5 |
| I_integrity | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | UNKNOWN: đầu miền 1/5 |
| A | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | UNKNOWN: đầu miền 1/5 |
| B | UNKNOWN | [1.8, 25] · LOW–CRITICAL · REVIEW | [9, 25] · MODERATE–CRITICAL · REVIEW | UNKNOWN: đầu miền 1/5 |

### MF-06 — baseline 1 · LOW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 1 | BOUNDARY | 1.08 · LOW | ±1, các yếu tố khác giữ nguyên |
| F | 1 | BOUNDARY | 1.12 · LOW | ±1, các yếu tố khác giữ nguyên |
| G | 1 | BOUNDARY | 1 · LOW | ±1, các yếu tố khác giữ nguyên |
| C | 1 | BOUNDARY | 2 · LOW | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 1 | BOUNDARY | 2 · LOW | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | 2 · LOW | ±1, các yếu tố khác giữ nguyên |
| B | 1 | BOUNDARY | 2 · LOW | ±1, các yếu tố khác giữ nguyên |

### MF-07 — baseline 25 · CRITICAL

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 23 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 22 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 5 | 21 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| C | 5 | 25 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 5 | 25 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| A | 5 | 25 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| B | 5 | 25 · CRITICAL | BOUNDARY | ±1, các yếu tố khác giữ nguyên |

### MF-08 — baseline 5 · LOW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 4.6 · LOW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 4.4 · LOW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 5 | 4.2 · LOW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| C | 1 | BOUNDARY | 10 · MODERATE | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 1 | BOUNDARY | 10 · MODERATE | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | 10 · MODERATE | ±1, các yếu tố khác giữ nguyên |
| B | 1 | BOUNDARY | 10 · MODERATE | ±1, các yếu tố khác giữ nguyên |

### MF-09 — baseline 10 · MODERATE

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 9.2 · MODERATE | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 8.8 · MODERATE | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 5 | 8.4 · MODERATE | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| C | 2 | 10 · MODERATE | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 2 | 10 · MODERATE | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |
| A | 2 | 10 · MODERATE | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |
| B | 2 | 10 · MODERATE | 15 · HIGH | ±1, các yếu tố khác giữ nguyên |

### MF-10 — baseline [5.4, 15] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [5.16, 13.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | [5.04, 13.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | UNKNOWN | 5.4 · MODERATE | 15 · HIGH | UNKNOWN: đầu miền 1/5 |
| C | 3 | [3.6, 10] · LOW–MODERATE · REVIEW | [7.2, 20] · MODERATE–CRITICAL · REVIEW | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| B | 2 | [5.4, 15] · MODERATE–HIGH · REVIEW | [5.4, 15] · MODERATE–HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |

### MF-11 — baseline [7.8, 13] · MODERATE–HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [7.32, 12.2] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | [7.08, 11.8] · MODERATE–HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 2 | [5.4, 9] · MODERATE · REVIEW | [10.2, 17] · HIGH–CRITICAL · REVIEW | ±1, các yếu tố khác giữ nguyên |
| C | 3 | [5.2, 13] · MODERATE–HIGH · REVIEW | [10.4, 13] · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| I_integrity | UNKNOWN | 7.8 · MODERATE | 13 · HIGH | UNKNOWN: đầu miền 1/5 |
| A | 1 | BOUNDARY | [7.8, 13] · MODERATE–HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| B | 2 | [7.8, 13] · MODERATE–HIGH · REVIEW | [7.8, 13] · MODERATE–HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |

### MF-12 — baseline 13 · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | 12.2 · HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 5 | 11.8 · HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| G | 2 | 9 · MODERATE · REVIEW | 17 · CRITICAL · REVIEW | ±1, các yếu tố khác giữ nguyên |
| C | 5 | [10.4, 13] · HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| I_integrity | UNKNOWN | 13 · HIGH | 13 · HIGH | UNKNOWN: đầu miền 1/5 |
| A | 1 | BOUNDARY | 13 · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| B | 2 | 13 · HIGH · REVIEW | 13 · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |

### MF-13 — baseline [1, 1] · LOW · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 1 | BOUNDARY | [1.08, 1.4] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |
| F | 1 | BOUNDARY | [1.12, 1.6] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |
| G | UNKNOWN | 1 · LOW | 1 · LOW | UNKNOWN: đầu miền 1/5 |
| C | 1 | BOUNDARY | [2, 2] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 1 | BOUNDARY | [2, 2] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | [2, 2] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |
| B | 1 | BOUNDARY | [2, 2] · LOW · REVIEW | ±1, các yếu tố khác giữ nguyên |

### MF-14 — baseline MISSING_ESSENTIAL_CONTEXT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| G | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |

### MF-15 — baseline INVALID_INPUT

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 0 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| F | 5 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| G | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| C | 3 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| I_integrity | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| A | 1 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |
| B | 2 | NOT_RUN | NOT_RUN | Thiếu context/input lỗi |

### MF-16 — baseline [12.96, 15.2] · HIGH · REVIEW

| Yếu tố | Gốc | −1 / đầu thấp | +1 / đầu cao | Cách đọc |
| --- | --- | --- | --- | --- |
| E | 5 | [11.68, 13.6] · HIGH · REVIEW | BOUNDARY | ±1, các yếu tố khác giữ nguyên |
| F | 3 | [11.04, 12.8] · HIGH · REVIEW | [14.88, 17.6] · HIGH–CRITICAL · REVIEW | ±1, các yếu tố khác giữ nguyên |
| G | UNKNOWN | 12.96 · HIGH | 15.2 · HIGH | UNKNOWN: đầu miền 4/5 |
| C | 4 | [9.72, 11.4] · MODERATE–HIGH · REVIEW | [16.2, 19] · HIGH–CRITICAL · REVIEW | ±1, các yếu tố khác giữ nguyên |
| I_integrity | 1 | BOUNDARY | [12.96, 15.2] · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| A | 1 | BOUNDARY | [12.96, 15.2] · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |
| B | 3 | [12.96, 15.2] · HIGH · REVIEW | [12.96, 15.2] · HIGH · REVIEW | ±1, các yếu tố khác giữ nguyên |

## 3. Kết luận độ nhạy cần review

Ở MF-03, G±1 đổi R ±2.24; F±1 đổi ±1.92; E−1 đổi −1.28, E+1 ngoài biên. C±1 đổi ±3.24; I_integrity/A/B ở các hướng hợp lệ chưa đổi max. C giảm 4→3 đưa R=9.72, nhãn MODERATE; gốc R=12.96 HIGH. Độ nhạy trọng số E/F ±10 điểm phần trăm chỉ ±0.64. Ưu tiên làm rõ rubric G và impact chi phối, không chỉ tinh chỉnh trọng số.

Các yếu tố impact dưới cực đại có thể không đổi score, nhưng cần evidence cho xử lý hậu quả. Một biến thể số không bảo đảm tương ứng một thay đổi thực tế độc lập. Các kết quả này chỉ phân tích mô hình đề xuất.

## 4. Cặp MF-03/MF-04 cần người dùng xác nhận

| Nội dung | MF-03 | MF-04 |
| --- | --- | --- |
| E/F/G | 5/3/4 | 3/4/4 |
| C/I_integrity/A/B | 4/1/1/3 | 4/4/3/4 |
| R chi tiết | 12.96 | 12.32 |
| Nhãn | HIGH | HIGH |
| Số chiều impact bằng 4 | 1 | 3 |
| Độ khả dĩ tiền điều kiện thực tế | UNKNOWN | UNKNOWN |

Quyết định review: **PENDING_USER_REVIEW**. Lựa chọn: ưu tiên MF-03 / MF-04 / ngang nhau / chưa đủ dữ liệu. Ghi lý do, người và thời điểm; không suy lựa chọn từ chênh lệch 0.64. MF-04 không kém MF-03 trên vector impact nhưng có P khác, nên đây không là lỗi tính toán; max đã làm mất thông tin độ rộng hậu quả. R không tự quyết định thứ tự ưu tiên chéo scenario.

## 5. Hai người chấm G độc lập

Đã chuẩn bị [phiếu A](risk-g-rating-a-v0.3.md) và [phiếu B](risk-g-rating-b-v0.3.md), mỗi phiếu 6 case tổng hợp. **NOT_RUN**: chưa có người chấm, không có kết quả độ lệch, tỷ lệ đồng thuận hoặc phân xử. Mỗi người dùng cùng rubric/gói thông tin và không xem điểm của người kia trước khi nộp. Không dùng một tác giả chấm hai lần làm bằng chứng độc lập.

Khi có kết quả: báo số ca cả hai cho số, số ca có UNKNOWN, tỷ lệ trùng G (mẫu số là ca cả hai cho số), bảng |G_A−G_B|, số lệch ≥2, xung đột coverage và mức risk. Lệch ≥2 hoặc đổi nhãn cần phân xử có reason; giữ bản chấm gốc. Không đặt ngưỡng đạt chuẩn thống kê cho mẫu nhỏ này.

## 6. Truy vết năm phản hồi

| Vấn đề | Sửa đổi | Còn thiếu |
| --- | --- | --- |
| CONDITIONAL/E và xếp hạng | R cho cùng scenario trước/sau; plausibility riêng; không rank bằng range | Review nhãn/horizon ngoài lab |
| Biên impact | Gate I_total=1 LOW, I_total=2 tối đa MODERATE; R giữ nguyên | Xác nhận chính sách ưu tiên |
| F/G và độ nhạy | F phản thực tế rõ; coverage/strength từng đường; ±1 toàn fixture | Hai người chấm G thực tế |
| UNKNOWN | Cận số/cận nhãn; impact max=5 suy ra được, vẫn review | Evidence thật |
| Ordinal/nguồn/nhập liệu/max | Hiển thị xấp xỉ; NIST/Cox kiểm tra; template E/F/G; cặp MF-03/MF-04 | Review người dùng/SME |

Nguồn và phạm vi đã đọc được ghi ở RM-01 v0.3 mục 8. Các thay đổi trên không phải hiệu chuẩn khoa học hoặc kiểm chứng lab. Bước 02 vẫn IN_PROGRESS.
