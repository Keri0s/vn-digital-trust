"""Interactive entry point for the one-time local administrator."""

from getpass import GetPassWarning, getpass
import sys
import warnings

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from vdt.core.local_bootstrap import BootstrapError, provision_admin, require_local_database
from vdt.core.rbac_catalog import CatalogError


class Command(BaseCommand):
    help = "Create the first VDT administrator in the synthetic local lab. Password is entered privately."

    def add_arguments(self, parser):
        parser.add_argument("--username")
        parser.add_argument("--display-name")
        parser.add_argument("--organization-code", default="ORG-ABC")
        parser.add_argument("--organization-name", default="ABC Trading (lab)")
        parser.add_argument("--database", default="default")

    def handle(self, *args, **options):
        try:
            require_local_database(options["database"])
            if not sys.stdin.isatty():
                raise CommandError("Open an interactive terminal. Passwords cannot be passed as arguments, environment variables or redirected input.")
            username = options["username"] or input("Tên đăng nhập VDT: ").strip()
            display_name = options["display_name"] or input("Tên hiển thị: ").strip()
            with warnings.catch_warnings():
                warnings.simplefilter("error", GetPassWarning)
                password = getpass("Mật khẩu (ít nhất 12 ký tự; không hiển thị): ")
                confirm = getpass("Nhập lại mật khẩu: ")
            if password != confirm:
                raise CommandError("Hai mật khẩu không khớp. Chưa tạo tài khoản.")
            result = provision_admin(username=username, display_name=display_name, password=password,
                organization_code=options["organization_code"], organization_name=options["organization_name"],
                using=options["database"])
            password = confirm = None
            self.stdout.write(self.style.SUCCESS(f"Đã tạo tài khoản VDT: {result.username}"))
            self.stdout.write("Quyền quản trị local không đặt ngày hết hạn; phiên đăng nhập vẫn có thời hạn riêng.")
            self.stdout.write("Môi trường giả lập; chưa có phê duyệt nghiệp vụ hoặc cấu hình CRM.")
        except (BootstrapError, CatalogError) as error:
            raise CommandError(str(error)) from error
        except ValidationError as error:
            raise CommandError(" ".join(error.messages)) from error
        except GetPassWarning:
            raise CommandError("Terminal không hỗ trợ nhập mật khẩu riêng tư. Chưa tạo tài khoản.") from None
        except DatabaseError:
            raise CommandError("Không thể hoàn tất giao dịch khởi tạo. Không in chi tiết database để bảo vệ thông tin tài khoản.") from None
        except (EOFError, KeyboardInterrupt):
            raise CommandError("Đã hủy; chưa tạo tài khoản.") from None
