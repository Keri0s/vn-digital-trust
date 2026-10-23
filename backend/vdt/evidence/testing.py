"""Explicit unit-test double. Application configuration must never import it."""

from .scanner import ScanResult


class FakeScanner:
    def __init__(self, result):
        if not isinstance(result, (ScanResult, Exception)):
            raise TypeError("An explicit test result or exception is required")
        self.result = result
        self.bytes_seen = b""
        self.calls = 0

    def scan(self, handle):
        self.calls += 1
        self.bytes_seen = handle.read()
        if isinstance(self.result, Exception):
            raise self.result
        return self.result
