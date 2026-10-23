# Kiểm chứng mốc đầu Bước 06 — 2026-10-23

## 1. Phạm vi và kết quả

Mã triển khai nằm trong `backend/`, kiểm thử trong `tests/unit/`, cách dựng môi trường trong `lab/local/`. Dữ liệu runtime và secrets nằm dưới `.runtime/`, bị Git và Docker build context loại trừ. Không có mật khẩu mẫu hay CRM account được seed.

| Nhóm kiểm chứng | Đã chạy | Kết quả |
| --- | --- | --- |
| Cấu hình strict JSON, trường bắt buộc, origin/RP, policy flags | 11 ca | Đạt |
| Policy authorization thuần, scope, assignment, expiry, identity independence | 15 ca | Đạt |
| RBAC seed provenance, đúng mapping, no-op và từ chối drift | 12 ca | Đạt |
| File thật trong thư mục tạm: hash, streaming cap, format, quarantine, promotion, lock, cleanup; scanner protocol giả lập | 25 ca | Đạt, gồm symlink trên Linux |
| Risk engine với 26 MF + 20 IP + 2 ca biên | 48 ca | Đạt |
| RiskComputed của 26 MF theo OpenAPI; PDF hợp lệ/mã hóa bằng pypdf đã cài | 3 ca, có subtests | Đạt |
| Django HTTP trong tiến trình, HTTPS redirect, CSRF/Origin, headers, host, endpoint chưa triển khai | 7 ca | Đạt |
| PostgreSQL thật: 106 bảng, bất biến, version, deferred payload, dấu thời gian, quyền runtime | 15 kiểm tra | Đạt |
| RBAC trên PostgreSQL: nạp 4/19/22, lặp không đổi, rollback drift, runtime chỉ đọc | 10 kiểm tra | Đạt |
| Django migration model drift | `makemigrations --check --dry-run` | No changes detected |
| Django deploy configuration check | `check --deploy` | Còn 2 cảnh báo W005/W021; không tắt cảnh báo |
| CRM config template preflight | Target `crm` | BLOCKED, 35 vấn đề được ghi trong JSON |

Nguồn chi tiết: [121 unit checks](unit-checks-v0.1.json), [15 database checks](database-checks-v0.1.json), [10 RBAC database checks](rbac-catalog-checks-v0.1.json). JSON ghi thời gian UTC, runtime và hash nguồn. Test runner không có mạng; DB runner chỉ dùng database phát triển riêng. Dữ liệu tổng hợp trong kiểm tra DB được rollback; danh mục RBAC đúng seed được giữ. `vdt_owner` là bootstrap/migration superuser của container local; app dùng `vdt_app` không có quyền quản trị, CREATE schema, DELETE/TRUNCATE lịch sử hoặc tắt trigger. App chỉ đọc ba bảng catalog. Quyền DB này chưa thay thế kiểm quyền nghiệp vụ.

## 2. Sửa từ kiểm chứng thực tế

1. DDL Bước 05 dùng `BEGIN/COMMIT`; migration runtime bỏ cặp ngoài vì Django đã quản lý transaction. Dùng `SET LOCAL search_path` và khôi phục `public, pg_catalog` trước khi Django ghi migration recorder. Lần đầu thiếu bước khôi phục làm recorder lỗi; transaction rollback. Migration sau sửa đã thành công trên PostgreSQL 17.11. DDL thiết kế gốc giữ nguyên.
2. Ánh xạ `AppUser.last_login` về đúng cột `last_login`. Authentication/session service chưa triển khai; cập nhật user sau này phải tuân thủ version/authorization guard, không dùng mặc định Django một cách ngầm định.
3. Bộ test file ban đầu trên Windows bỏ qua symlink do thiếu đặc quyền. Chạy lại Linux với code chỉ đọc và working directory `/tmp` đã kiểm cả ca này. Lần đầu dùng working directory dưới mount chỉ đọc làm test setup thất bại; không thay đổi quyền kho tệp để xử lý.
4. HTTP test POST hợp lệ được bổ sung Origin đúng; request thiếu CSRF hoặc có Origin khác vẫn bị từ chối. Chưa có kiểm thử trình duyệt/TLS thật.

## 3. Tương thích fixture lịch sử

Fixture IP cũ dùng `score_change=NOT_COMPARABLE` cho cả trường hợp cùng context nhưng điểm chưa xác định. API Bước 05 tách `comparability=COMPARABLE` và `R_progress=UNDETERMINED`. Adapter kiểm thử ghi rõ phép ánh xạ này trong `tests/unit/test_risk_engine.py`; không sửa fixture, không biến khoảng điểm thành giá trị đơn. Các trường hợp context không tương đương vẫn NOT_COMPARABLE. Kiểm tra schema xác nhận DTO RiskComputed; chưa có DTO/persistence tích hợp cho toàn bộ API.

## 4. Giới hạn phải giữ trong mọi báo cáo

- Đã nạp danh mục RBAC; chưa provisioning user/assignment hoặc triển khai auth/session API, middleware Policy gate và recheck thực tế, upload/download API, DB-file/job transaction hoặc reverse proxy. App service chưa được bật; Compose không publish cổng app trực tiếp.
- File checks dùng `FakeScanner` và socket fixture; chưa chứng minh phát hiện malware, signature update, thời gian quét hoặc ClamAV daemon thật. PDF hợp lệ/mã hóa đã được kiểm bằng pypdf; không render tài liệu tải lên.
- HSTS subdomains/preload chưa bật vì domain/TLS local còn chưa dựng. Hai cảnh báo W005/W021 được giữ; không tuyên bố production-ready.
- Chưa kiểm concurrency/revoke giữa giao dịch, crash reconciliation, backup/restore, export/as_of, resource budget, hoặc workflow end-to-end.
- Chưa có CRM/VPN/receiver/WebAuthn thật. 35 lỗi preflight là trạng thái template chưa đủ cấu hình, không phải test thất bại bị bỏ qua. Ví dụ 120/5/900 chưa là cấu hình hiệu lực.
- FLOW, TC-01 và VALID-G-01 vẫn NOT_RUN; không có SME approval, calibration hoặc evidence CRM. Bước 06 giữ IN_PROGRESS.

## 5. Phiên bản đã dùng

Python 3.13.17 / Django 5.2.18 / DRF 3.16.1 / psycopg 3.3.6 / pypdf 6.21.2; PostgreSQL 17.11. Image gốc pin theo digest trong Dockerfile/Compose; 17 package pin kèm SHA-256 trong requirements.lock. Build đã cài bằng `--require-hashes`. Chọn bản vá trong dòng stack của Bước 05; tham chiếu [Django](https://www.djangoproject.com/download/) và [DRF 3.16](https://www.django-rest-framework.org/community/3.16-announcement/). Phiên bản là thông tin của lần chạy này, không khẳng định luôn mới nhất.
