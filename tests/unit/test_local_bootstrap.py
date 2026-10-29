"""Bootstrap input and interactive boundary checks; no database is opened."""
import io
import os
from getpass import GetPassWarning
from unittest.mock import MagicMock, patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vdt.settings")
os.environ.setdefault("VDT_SECRET_KEY", "unit-test-only-unused-as-deployment-secret-0123456789")
os.environ.setdefault("PGUSER", "unit-test-no-connection")
os.environ.setdefault("PGPASSWORD", "unit-test-no-connection")
import django
django.setup()

from django.core.exceptions import ValidationError
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings
from vdt.core.local_bootstrap import BootstrapError, require_local_database, validate_inputs
from vdt.core.management.commands.bootstrap_local_admin import Command


class LocalBootstrapTests(SimpleTestCase):
    def inputs(self, **changes):
        values = dict(username="lab-admin", display_name="Quản trị thử nghiệm",
                      password="Synthetic-Only-Password-8361", organization_code="ORG-ABC",
                      organization_name="ABC Trading (lab)")
        values.update(changes)
        return validate_inputs(**values)

    def test_accepts_unicode_display_name(self):
        self.assertEqual(self.inputs()[1], "Quản trị thử nghiệm")

    def test_rejects_username_beyond_contract_limit(self):
        with self.assertRaises(BootstrapError):
            self.inputs(username="a" * 151)

    def test_rejects_empty_display_name_and_controls(self):
        for value in ("", " ", "Admin\nOther", "a" * 201):
            with self.subTest(value=value), self.assertRaises(BootstrapError):
                self.inputs(display_name=value)

    def test_rejects_invalid_username(self):
        with self.assertRaises(ValidationError):
            self.inputs(username="name/../../admin")

    def test_enforces_password_length(self):
        for value in ("short", " " * 20, "x" * 1025):
            with self.subTest(length=len(value)), self.assertRaises(BootstrapError):
                self.inputs(password=value)

    def test_uses_django_numeric_password_validator(self):
        with self.assertRaises(ValidationError):
            self.inputs(password="938572915037592816")

    @override_settings(VDT_LOCAL_FOUNDATION_ONLY=False)
    def test_opt_in_required_before_database(self):
        with patch("vdt.core.local_bootstrap.connections") as connections:
            with self.assertRaisesRegex(BootstrapError, "LOCAL_OPT_IN_REQUIRED"):
                require_local_database()
            connections.__getitem__.assert_not_called()

    @override_settings(VDT_LOCAL_FOUNDATION_ONLY=True)
    def test_actual_database_name_is_verified(self):
        with patch("vdt.core.local_bootstrap.connections") as connections:
            database = connections.__getitem__.return_value
            database.vendor = "postgresql"
            database.cursor.return_value.__enter__.return_value.fetchone.return_value = ("production",)
            with self.assertRaisesRegex(BootstrapError, "LOCAL_DATABASE_REQUIRED"):
                require_local_database()

    def options(self):
        return dict(username="lab-admin", display_name="Lab Admin", organization_code="ORG-ABC",
                    organization_name="ABC Trading (lab)", database="default")

    def test_command_rejects_noninteractive_stdin(self):
        module = "vdt.core.management.commands.bootstrap_local_admin"
        with patch(module + ".require_local_database"), patch(module + ".sys.stdin.isatty", return_value=False), \
             patch(module + ".getpass") as secret_prompt, patch(module + ".provision_admin") as provision:
            with self.assertRaises(CommandError):
                Command(stdout=io.StringIO()).handle(**self.options())
            secret_prompt.assert_not_called()
            provision.assert_not_called()

    def test_command_refuses_password_mismatch(self):
        module = "vdt.core.management.commands.bootstrap_local_admin"
        with patch(module + ".require_local_database"), patch(module + ".sys.stdin.isatty", return_value=True), \
             patch(module + ".getpass", side_effect=["synthetic-one", "synthetic-two"]), \
             patch(module + ".provision_admin") as provision:
            with self.assertRaises(CommandError):
                Command(stdout=io.StringIO()).handle(**self.options())
            provision.assert_not_called()

    def test_command_refuses_echo_fallback(self):
        module = "vdt.core.management.commands.bootstrap_local_admin"
        with patch(module + ".require_local_database"), patch(module + ".sys.stdin.isatty", return_value=True), \
             patch(module + ".getpass", side_effect=GetPassWarning("no echo support")), \
             patch(module + ".provision_admin") as provision:
            with self.assertRaises(CommandError):
                Command(stdout=io.StringIO()).handle(**self.options())
            provision.assert_not_called()
