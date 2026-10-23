# Lưu image/data Docker tại ổ D — 2026-10-23

**Yêu cầu trực tiếp:** Người dùng đề nghị lưu image/data trong thư mục project vì ổ C sắp đầy. Đã hoàn tất chuyển hai đĩa Docker vào `D:\Projects\vn-digital-trust\.runtime\docker-desktop`.

| Nội dung | Vị trí vật lý hiện tại | Kiểm chứng |
| --- | --- | --- |
| Image, container layers, build cache, named volume PostgreSQL của WSL backend | `.runtime/docker-desktop/wsl-disk/docker_data.vhdx` | SHA-256 bản sao khớp trước khởi động; 4 image và volume còn đầy đủ; DB chạy lại và 15/15 kiểm tra đạt |
| Đĩa Docker VMM đang không được sử dụng | `.runtime/docker-desktop/vm-data/DockerDesktop.vhdx` | SHA-256 bản sao khớp; chưa chạy backend VMM |
| Bản sao SQL trước di chuyển | `.runtime/docker-desktop/migration-backup/vdt-before-storage-move.sql` | Đã xuất và sao chép thành công; chưa kiểm restore |
| Metadata di chuyển | `.runtime/docker-desktop/migration-record.json` | Ghi hash trước/sau sao chép và trạng thái xóa bản gốc tạm |

Hai thư mục cũ dưới `C:\Users\trant\AppData\Local\Docker` hiện là **NTFS junction** trỏ tới hai thư mục trên ổ D. Vì vậy đường dẫn được Docker hiển thị có thể vẫn bắt đầu bằng C, nhưng bytes image/data được lưu ở D. Dùng cơ chế đường dẫn tương thích của Windows; chưa đổi Disk image location trong giao diện Docker. Windows hỗ trợ junction nối thư mục giữa các ổ local. [Microsoft](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions)

## Quy trình đã thực hiện

1. Xác nhận chỉ có container DB của dự án, WSL backend và một named volume; ghi inventory image/volume.
2. Xuất database vào ổ D, dừng PostgreSQL/Docker sạch sẽ, xác nhận WSL dừng.
3. Sao chép từng VHDX sang D, đối chiếu SHA-256, đổi tên thư mục gốc thành bản dự phòng tạm và tạo junction.
4. Khởi động Docker/DB, xác nhận image IDs và volume được giữ; chạy lại 15 kiểm tra PostgreSQL, đạt cả 15.
5. Chỉ xóa đúng hai VHDX dự phòng trên C sau kiểm hash và xác nhận junction/DB. Không prune image, volume hoặc dữ liệu khác.

Đã giải phóng **3.675 GiB** theo tổng kích thước hai file cũ. Sau bước này ổ C còn **24.247 GiB**, ổ D còn **83.010 GiB**; đây là số đo tại thời điểm chuyển, sẽ thay đổi khi sử dụng. Bản ghi không có secrets: [JSON](docker-storage-move-v0.1.json).

## Vận hành tiếp

- Đây là nơi lưu **toàn bộ kho image/data của Docker Desktop trên tài khoản này**, gồm cả image tạo sau này. Không di chuyển, đổi tên hoặc xóa thư mục project/`.runtime/docker-desktop` khi còn dùng Docker. Nếu cần chuyển tiếp, dừng Docker và giữ nguyên dữ liệu cùng đường dẫn liên kết.
- `.runtime/` bị Git và Docker build context loại trừ. Không đóng gói VHDX, secrets hoặc database backup vào gói source/report.
- Bộ cài Docker, log/cấu hình nhỏ và đĩa hệ thống WSL `wsl/main/ext4.vhdx` khoảng 0.094 GiB vẫn ở C. Phần này không phải kho image/named volume đã chuyển.
- Không bind trực tiếp PostgreSQL data directory lên thư mục NTFS. Named volume vẫn giữ filesystem Linux bên trong VHDX, nay đặt tại D.
- Sau reset/reinstall Docker hoặc thay đổi backend, kiểm lại junction và vị trí đĩa trước khi pull/build lớn. Đường chuyển chính thức qua giao diện là Settings → Resources → Advanced → Disk image location. [Docker WSL storage](https://docs.docker.com/desktop/features/wsl/)
- SQL dump trước di chuyển hỗ trợ khôi phục dữ liệu; chưa thay thế bài kiểm backup/restore của Bước 06.
