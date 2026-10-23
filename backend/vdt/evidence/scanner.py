"""Fail-closed local clamd INSTREAM client; no TCP or path-based scan command.

Protocol reference: https://docs.clamav.net/manual/Usage/ClamdProtocol.html
The deployment must configure clamd's clock/timezone consistently, alert on
encrypted/oversized/unscannable content and set StreamMaxLength >= upload cap.
LocalEvidenceStorage.scan supplies the cross-process sequential scan guard.
"""

import re
import socket
import struct
import time
from dataclasses import dataclass
from datetime import datetime, timezone, tzinfo
from enum import Enum
from typing import BinaryIO, Protocol

from .errors import ScannerUnavailable, StaleSignatures


class ScanVerdict(str, Enum):
    CLEAN = "CLEAN"
    INFECTED = "INFECTED"


@dataclass(frozen=True)
class ScanResult:
    verdict: ScanVerdict
    engine_version: str
    signature_version: str
    signature_published_at: datetime
    scanned_at: datetime

    def valid_at(self, now, max_age_seconds):
        try:
            return (isinstance(self.verdict, ScanVerdict) and bool(self.engine_version)
                    and bool(self.signature_version)
                    and 0 <= (now - self.signature_published_at).total_seconds() < max_age_seconds
                    and 0 <= (now - self.scanned_at).total_seconds() < max_age_seconds)
        except (TypeError, AttributeError):
            return False


class Scanner(Protocol):
    def scan(self, handle: BinaryIO) -> ScanResult: ...


class ClamdScanner:
    def __init__(self, socket_path, *, expected_engine_version,
                 expected_signature_version, timeout_seconds=60,
                 signature_max_age_seconds=86400, daemon_timezone: tzinfo = timezone.utc,
                 clock=None):
        if (not isinstance(socket_path, str) or not socket_path.startswith("/")
                or "\x00" in socket_path or not expected_engine_version
                or not expected_signature_version or timeout_seconds <= 0
                or signature_max_age_seconds <= 0 or daemon_timezone is None):
            raise ScannerUnavailable()
        self._socket_path = socket_path
        self._engine = str(expected_engine_version)
        self._signature = str(expected_signature_version)
        self._timeout = timeout_seconds
        self._max_age = signature_max_age_seconds
        self._timezone = daemon_timezone
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def _remaining(deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ScannerUnavailable()
        return remaining

    def _exchange(self, command, deadline, handle=None):
        if not hasattr(socket, "AF_UNIX"):
            raise ScannerUnavailable()
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(self._remaining(deadline))
                connection.connect(self._socket_path)
                connection.settimeout(self._remaining(deadline))
                connection.sendall(command)
                if handle is not None:
                    handle.seek(0)
                    while True:
                        chunk = handle.read(64 * 1024)
                        if not chunk:
                            break
                        connection.settimeout(self._remaining(deadline))
                        connection.sendall(struct.pack(">I", len(chunk)) + chunk)
                    connection.settimeout(self._remaining(deadline))
                    connection.sendall(b"\x00\x00\x00\x00")
                reply = bytearray()
                while True:
                    connection.settimeout(self._remaining(deadline))
                    chunk = connection.recv(1024)
                    if not chunk:
                        break
                    reply.extend(chunk)
                    if len(reply) > 4096:
                        raise ScannerUnavailable()
                # Exactly one complete record is accepted, never a partial 'OK'.
                if not reply.endswith(b"\x00") or reply.count(0) != 1:
                    raise ScannerUnavailable()
                return bytes(reply[:-1]).decode("ascii", errors="strict")
        except (OSError, UnicodeError, ValueError, AttributeError):
            raise ScannerUnavailable() from None

    def _version(self, deadline):
        reply = self._exchange(b"zVERSION\x00", deadline)
        match = re.fullmatch(r"ClamAV ([0-9][0-9A-Za-z.+~-]*)/([0-9]+)/(.+)", reply)
        if match is None or match[1] != self._engine or match[2] != self._signature:
            raise ScannerUnavailable()
        try:
            published = datetime.strptime(match[3], "%a %b %d %H:%M:%S %Y").replace(tzinfo=self._timezone)
            age = (self._clock() - published).total_seconds()
        except (ValueError, TypeError):
            raise ScannerUnavailable() from None
        if age < 0 or age >= self._max_age:
            raise StaleSignatures()
        return match[1], match[2], published

    def scan(self, handle):
        deadline = time.monotonic() + self._timeout
        before = self._version(deadline)
        reply = self._exchange(b"zINSTREAM\x00", deadline, handle)
        if reply == "stream: OK":
            verdict = ScanVerdict.CLEAN
        elif re.fullmatch(r"stream: .+ FOUND", reply):
            verdict = ScanVerdict.INFECTED
        else:
            raise ScannerUnavailable()
        after = self._version(deadline)
        if before != after:
            raise ScannerUnavailable()
        return ScanResult(verdict, *after, self._clock())
