# Bước 06 — triển khai prototype và lab local

**Cập nhật 2026-10-23 · IN_PROGRESS · Mốc đầu: nền ứng dụng và các module độc lập.**

Người dùng đã yêu cầu bắt đầu Bước 06 và chọn chuẩn bị lab local vì chưa có CRM. Đây là kết quả khởi động triển khai; chưa hoàn thành Bước 06 và chưa có ứng dụng nghiệp vụ dùng được từ trình duyệt.

## Đã có

| Hạng mục | Kết quả thực tế | Giới hạn |
| --- | --- | --- |
| Môi trường | Image Python 3.13.17, Django 5.2.18, DRF 3.16.1; PostgreSQL 17.11; dependency hash lock | Docker phát triển local; chưa nghiệm thu deployment/TLS |
| Database | Migration 106 bảng; 15/15 kiểm tra PostgreSQL đạt | Chưa seed SME/user; chưa kiểm giao dịch cạnh tranh/restore |
| Danh mục RBAC | Đã nạp 4 role, 19 permission, 22 liên kết; 12 unit + 10 PostgreSQL checks đạt | Chưa tạo role assignment hoặc cấp quyền cho tài khoản; xem [biên bản](rbac-catalog-v0.1.md) |
| Risk | RM-01, UNKNOWN/ranges, max G theo đường và impact comparison; 48 kiểm thử | Confirmation phải lấy từ dịch vụ có quyền; chưa có API hoặc persistence |
| Policy | 15 kiểm thử phạm vi, assignment, hết hạn, độc lập actor | Hàm thuần; chưa nối middleware, database hay recheck lúc commit/stream |
| Evidence | Stage/hash/format/scan protocol/promote/read/cleanup; 25 kiểm thử | Scanner dùng test double; chưa chạy clamd hoặc tích hợp DB/job/upload |
| Cấu hình | 11 kiểm thử; template CRM bị chặn với 35 vấn đề cấu hình | Năm trường AUTH-CRM-01 còn chưa đặt; không tự dùng 120/5/900 |
| Kiểm tra bổ sung | 3 ca contract/parser và 7 ca HTTP trong tiến trình | Không chứng minh proxy TLS, session/login hay luồng nghiệp vụ hoạt động |

**Tổng: 121/121 unit/contract/HTTP checks đạt trên Linux, 0 skip; 15/15 database foundation checks và 10/10 RBAC database checks đạt.** Health endpoint chỉ chứng minh hàm xử lý đang trả lời. Các endpoint nghiệp vụ trả `503 PROTOTYPE_NOT_READY`; request ghi thiếu CSRF bị từ chối. Chưa chạy dịch vụ app lâu dài; database local đang chạy, chỉ mở ở `127.0.0.1:55432`.

## Hồ sơ và cách tái lập

- [Báo cáo kiểm chứng và giới hạn](validation-v0.1.md).
- [Kết quả 121 kiểm thử và hash mã nguồn](unit-checks-v0.1.json).
- [Kết quả PostgreSQL](database-checks-v0.1.json).
- [Kết quả RBAC PostgreSQL](rbac-catalog-checks-v0.1.json).
- [Nguồn migration](schema-provenance-v0.1.json), [dependency lock provenance](dependency-lock-v0.1.json).
- [Cách dựng và kiểm tra local](../../lab/local/README.md).
- [Phương án CRM/lab local](local-crm-lab-plan-v0.1.md).
- [Biên bản chuyển image/data Docker sang thư mục dự án ổ D](docker-storage-v0.1.md).
- [Kế hoạch chung, mục 29](../planning/execution-plan-v0.1.md).

## Mốc triển khai tiếp theo

1. Tạo tài khoản local với mật khẩu do operator đặt; triển khai login/logout, idle/absolute expiry và thu hồi phiên. Gán role/scope/assignment có hiệu lực theo thời gian thực bằng workflow kiểm quyền; danh mục quyền đã nạp không tự tạo các grant này.
2. Tích hợp Policy gate với dữ liệu scope/assignment hiện hành và khóa authorization trong transaction; kiểm deny/read/write/commit/revoke. Không cho client tự xác nhận factor hoặc scope.
3. Dựng Caddy/TLS và kiểm Browser → Reverse proxy → Policy gate; không mở upload trước khi có gate, scanner, giới hạn stream và transaction lifecycle đầy đủ.
4. Nối inventory/context/scenario → evidence/control/risk → review/treatment/retest/report; tiếp tục các gate idempotency, OCC, audit, snapshot/as_of và closure.
5. Dựng CRM local riêng, chốt cấu hình có provenance, chạy FLOW-01…10, T01–T24, VALID-G-01 và các kiểm tra lỗi/restore/tài nguyên.

FLOW-01…10, T01–T24, VALID-G-01 **NOT_RUN**. Phiếu chấm G A/B trống; chưa có evidence CRM hoặc hiệu chuẩn SME. MF-03/MF-04 vẫn **NOT_RANKED**, chưa có phê duyệt ưu tiên SME. Kết quả tính toán fixture không phải nghiệm thu nghiệp vụ.
