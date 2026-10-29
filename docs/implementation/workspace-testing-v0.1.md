# Tái lập kiểm thử workspace v0.1

Chạy từ `D:\Projects\vn-digital-trust`. Docker Desktop cần đang chạy và `.runtime/local.env` đã có. Giữ image/volume tại ổ D theo thiết lập hiện có. Những lệnh sau chỉ tạo/dọn project **vdt-workspace-test**, tách khỏi database thật **vdt-step06**.

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.workspace-test.yaml run --rm check
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.workspace-test.yaml down
```

Runner từ chối nếu không phải `testdb`, database/cờ local/test không đúng hoặc database test đã có tài khoản. Database dùng tmpfs; lệnh down dọn dữ liệu kiểm thử. Không dùng compose.yaml vận hành thay cho hai file test. Báo cáo `.runtime/checks/workspace-checks.json` có 59 kiểm tra mặc định; lần nghiệm chứng có thêm chuẩn bị browser fixture nên là 60.

Browser QA dùng thêm overlay `compose.access-test.yaml` **trước** `compose.workspace-test.yaml` và profile `browser-qa`. Cổng 8444 tách với 8443; chứng chỉ lấy từ CA lab hiện có. Chỉ dùng tài khoản tổng hợp được runner tạo trong testdb. Verifier browser là PBKDF2 salted hash chuyển qua stdin ẩn/môi trường tạm; không ghi plaintext vào file, lệnh hoặc báo cáo. `set_workspace_browser_verifier.py` từ chối database vận hành và tập tài khoản khác bộ test. Khi kết thúc, dọn project đúng ba file:

```powershell
docker compose --env-file .runtime/local.env -f lab/local/compose.auth-test.yaml -f lab/local/compose.access-test.yaml -f lab/local/compose.workspace-test.yaml --profile browser-qa down
```

Unit chạy bằng service `unit-check` trong compose.yaml. Hồi quy assessment dùng auth-test + assessment-test; auth dùng auth-test riêng. Không chạy lại runner trên database test đã có fixture; kết thúc đúng project test trước khi tái lập từ đầu.

Script HTTPS nền hiện dùng **Windows PowerShell 5.1**: `powershell.exe -NoProfile -File lab/local/verify_https.ps1`. PowerShell 7 trả header cookie dạng mảng khiến helper boolean cũ lỗi; đó là giới hạn runner, không phải lỗi HTTPS của ứng dụng. Bộ kiểm tra workspace sau triển khai ở [verify-workspace-https-v0.1.ps1](verify-workspace-https-v0.1.ps1) giải mã tài nguyên bằng UTF-8 trước khi so sánh nguồn. Không bỏ qua kiểm tra chứng chỉ.

Kết quả kiểm thử này không thay thế nghiệm thu CRM hoặc các FLOW/TC/VALID-G. Ảnh browser trong mốc này chỉ dùng dữ liệu tổng hợp.
