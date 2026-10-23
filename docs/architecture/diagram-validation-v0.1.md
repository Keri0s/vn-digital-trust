# Kiểm tra sơ đồ kiến trúc v0.1

**Ngày:** 2026-10-18. **Phạm vi:** thiết kế, không phải test runtime/CRM/lab.

Nguồn `container-v0.1.puml`, `deployment-v0.1.puml`, `evidence-decision-flow-v0.1.puml` được render trực tiếp bằng PlantUML 1.2026.8 với Java 17.0.18, UTF-8, headless và `-failfast2`; cả SVG và PNG trả exit code 0. Đã mở đọc ba PNG sau render: container cho thấy VDT tách CRM/lab và evidence store được gate; deployment cho thấy một host/VM với metadata, evidence, backup riêng; sequence cho thấy nhánh deny, verification, mixed failure + unknown, thiếu evidence, review tùy chọn và retest. Nhãn và mũi tên chính không bị cắt. Đây là kiểm tra hình ảnh thiết kế, chưa xác minh hành vi ứng dụng.

| Nguồn | SVG | PNG |
| --- | --- | --- |
| [Container](container-v0.1.puml) | [Mở SVG](container-v0.1.svg) | [Mở PNG](container-v0.1.png) |
| [Deployment](deployment-v0.1.puml) | [Mở SVG](deployment-v0.1.svg) | [Mở PNG](deployment-v0.1.png) |
| [Evidence/decision](evidence-decision-flow-v0.1.puml) | [Mở SVG](evidence-decision-flow-v0.1.svg) | [Mở PNG](evidence-decision-flow-v0.1.png) |

Đối chiếu bằng văn bản trong [kiến trúc mục 6](architecture-technical-v0.1.md) bao phủ SC-01/SC-02 và FLOW-01…10. FLOW/TC vẫn NOT_RUN; VALID-G-01 vẫn NOT_RUN.
