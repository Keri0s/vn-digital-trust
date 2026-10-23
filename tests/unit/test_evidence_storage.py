"""Real temporary files, harmless bytes, and explicit scanner doubles only."""

import hashlib
import io
import os
import socket
import struct
import tempfile
import unittest
import zlib
from contextlib import contextmanager
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

from vdt.evidence import (CleanupLease, ClamdScanner, EvidenceLimits, HashMismatch,
                          InvalidFile, LocalEvidenceStorage, MalwareDetected,
                          MetadataTooLarge, ScannerUnavailable, ScanResult,
                          ScanVerdict, StaleSignatures, StorageIntegrityError,
                          StorageUnavailable, UnsafeStorageKey, UploadTooLarge)
from vdt.evidence.testing import FakeScanner


class EvidenceStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "private-evidence"
        self.now = datetime.now(timezone.utc)
        self.limits = EvidenceLimits(max_file_bytes=1024, minimum_free_disk_bytes=0,
                                     staging_orphan_grace_seconds=30)
        self.storage = LocalEvidenceStorage(self.root, self.limits, clock=lambda: self.now)

    def stage(self, data=b"harmless log\n", **kwargs):
        defaults = dict(filename="events.log", declared_mime="text/plain", metadata={"source": "unit"})
        defaults.update(kwargs)
        return self.storage.stage((data[:3], data[3:]), **defaults)

    def scanner(self, verdict=ScanVerdict.CLEAN):
        return FakeScanner(ScanResult(verdict, "UNIT-TEST", "UNIT-TEST",
                                      self.now - timedelta(hours=1), self.now))

    def test_stream_hash_private_uuid_and_same_handle_download(self):
        payload = b"harmless log\n"
        staged = self.stage(payload, expected_sha256=hashlib.sha256(payload).hexdigest())
        self.assertEqual(UUID(staged.storage_key).version, 4)
        self.assertEqual(staged.size_bytes, len(payload))
        self.assertEqual(staged.sha256, hashlib.sha256(payload).hexdigest())
        self.assertNotIn(str(self.root), str(asdict(staged)))
        scanner = self.scanner()
        stored = self.storage.promote(self.storage.scan(staged, scanner))
        self.assertEqual(scanner.bytes_seen, payload)
        self.assertFalse((self.root / "quarantine" / stored.storage_key).exists())
        with self.storage.open_verified(stored.storage_key, stored.sha256, stored.size_bytes) as handle:
            self.assertEqual(handle.read(), payload)
        self.assertNotIn("COMMITTED", asdict(stored))

    def test_oversize_stream_enforced_without_content_length_and_deleted(self):
        with self.assertRaises(UploadTooLarge):
            self.stage(b"x" * 1025)
        self.assertEqual(list((self.root / "quarantine").iterdir()), [])
        self.assertEqual(list((self.root / "objects").iterdir()), [])

    def test_default_twenty_mib_limit_against_actual_streamed_bytes(self):
        storage = LocalEvidenceStorage(self.root, EvidenceLimits(minimum_free_disk_bytes=0))
        def chunks():
            for _ in range(20):
                yield b"x" * (1024 * 1024)
            yield b"x"
        with self.assertRaises(UploadTooLarge):
            storage.stage(chunks(), filename="a.log", declared_mime="text/plain", metadata={})
        self.assertEqual(list((self.root / "quarantine").iterdir()), [])

    def test_hash_mismatch_cleans_unfinished_bytes(self):
        with self.assertRaises(HashMismatch):
            self.stage(expected_sha256="0" * 64)
        self.assertEqual(list((self.root / "quarantine").iterdir()), [])

    def test_stream_exception_cleans_unfinished_bytes(self):
        def interrupted():
            yield b"partial"
            raise ConnectionError("client gone")
        with self.assertRaises(StorageUnavailable):
            self.storage.stage(interrupted(), filename="a.txt", declared_mime="text/plain", metadata={})
        self.assertEqual(list((self.root / "quarantine").iterdir()), [])

    def test_metadata_64_kib_cap_before_consuming_stream(self):
        called = []
        def chunks():
            called.append(True)
            yield b"text"
        with self.assertRaises(MetadataTooLarge):
            self.storage.stage(chunks(), filename="a.txt", declared_mime="text/plain",
                               metadata={"value": "x" * 65536})
        self.assertEqual(called, [])

    def test_metadata_canonical_digest(self):
        first = self.stage(metadata={"b": 2, "a": 1})
        second = self.stage(metadata={"a": 1, "b": 2})
        self.assertEqual(first.metadata_sha256, second.metadata_sha256)

    def test_path_names_and_non_uuid_storage_keys_rejected(self):
        for filename in ("../../outside.txt", "a\\b.txt", "C:escape.txt", "bad\x00.txt"):
            with self.subTest(filename=repr(filename)), self.assertRaises(InvalidFile):
                self.stage(filename=filename)
        for key in ("../outside", "C:\\outside", "objects/a", "a" * 32):
            with self.subTest(key=key), self.assertRaises(UnsafeStorageKey):
                with self.storage.open_verified(key, "0" * 64, 1):
                    pass

    def test_no_clean_default_and_error_keeps_uncommitted(self):
        staged = self.stage()
        for scanner in (None, FakeScanner(ScannerUnavailable())):
            with self.assertRaises(ScannerUnavailable):
                self.storage.scan(staged, scanner)
        with self.assertRaises(ScannerUnavailable):
            self.storage.promote(staged)
        self.assertTrue((self.root / "quarantine" / staged.storage_key).exists())
        self.assertEqual(list((self.root / "objects").iterdir()), [])

    def test_rejected_scan_keeps_quarantine_unpublished(self):
        staged = self.stage()
        with self.assertRaises(MalwareDetected):
            self.storage.scan(staged, self.scanner(ScanVerdict.INFECTED))
        self.assertTrue((self.root / "quarantine" / staged.storage_key).exists())
        self.assertEqual(list((self.root / "objects").iterdir()), [])

    def test_stale_scan_result_and_stale_before_promotion_deny(self):
        staged = self.stage()
        old = ScanResult(ScanVerdict.CLEAN, "UNIT", "UNIT", self.now - timedelta(days=1), self.now)
        with self.assertRaises(StaleSignatures):
            self.storage.scan(staged, FakeScanner(old))
        scanned = self.storage.scan(staged, self.scanner())
        self.now += timedelta(days=1)
        with self.assertRaises(StaleSignatures):
            self.storage.promote(scanned)

    def test_changed_bytes_after_scan_block_promotion(self):
        scanned = self.storage.scan(self.stage(), self.scanner())
        (self.root / "quarantine" / scanned.storage_key).write_bytes(b"different")
        with self.assertRaises(StorageIntegrityError):
            self.storage.promote(scanned)
        self.assertEqual(list((self.root / "objects").iterdir()), [])

    def test_existing_final_object_never_overwritten(self):
        scanned = self.storage.scan(self.stage(), self.scanner())
        target = self.root / "objects" / scanned.storage_key
        target.write_bytes(b"existing immutable object")
        with self.assertRaises(StorageUnavailable):
            self.storage.promote(scanned)
        self.assertEqual(target.read_bytes(), b"existing immutable object")
        self.assertTrue((self.root / "quarantine" / scanned.storage_key).exists())

    def test_corrupt_final_file_denies_download(self):
        stored = self.storage.promote(self.storage.scan(self.stage(), self.scanner()))
        (self.root / "objects" / stored.storage_key).write_bytes(b"corrupt")
        with self.assertRaises(StorageIntegrityError):
            with self.storage.open_verified(stored.storage_key, stored.sha256, stored.size_bytes):
                self.fail("Corrupt bytes were exposed")

    def test_mime_and_signature_validation(self):
        invalid = [(b"<html>unsafe</html>", "a.txt", "text/plain"),
                   (b"<svg></svg>", "a.txt", "text/plain"),
                   (b"MZpretend", "a.log", "text/plain"),
                   (b"PK\x03\x04zip", "a.txt", "text/plain"),
                   (b"not json", "a.json", "application/json"),
                   (b'{"x":NaN}', "a.json", "application/json"),
                   (b"\xfftext", "a.log", "text/plain"),
                   (b"%PDF-1.7\n%%EOF", "a.pdf", "application/pdf"),
                   (b"text", "a.exe", "text/plain"),
                   (b"text", "a.txt", "image/png")]
        for data, filename, mime in invalid:
            with self.subTest(filename=filename, data=data), self.assertRaises(InvalidFile):
                self.stage(data, filename=filename, declared_mime=mime)
        self.assertEqual(self.stage(b'{"ok":true}', filename="a.json", declared_mime="application/json").mime,
                         "application/json")
        self.assertEqual(self.stage(b"a,b\n1,2\n", filename="a.csv", declared_mime="text/plain").mime, "text/csv")

    def test_png_header_crc_and_dimensions(self):
        def chunk(kind, value):
            return struct.pack(">I", len(value)) + kind + value + struct.pack(">I", zlib.crc32(kind + value))
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))
        self.assertEqual(self.stage(png, filename="a.png", declared_mime="image/png").mime, "image/png")
        with self.assertRaises(InvalidFile):
            self.stage(png[:-5], filename="a.png", declared_mime="image/png")

    def test_cleanup_requires_expired_unreferenced_orphan_and_grace(self):
        staged = self.stage()
        old = self.now - timedelta(hours=2)
        path = self.root / "quarantine" / staged.storage_key
        os.utime(path, (old.timestamp(), old.timestamp()))
        calls = []
        lease = CleanupLease(old, old, "ORPHANED", False)
        @contextmanager
        def guard(key):
            calls.append(key)
            yield lease
        for change in (dict(lease_expires_at=self.now + timedelta(seconds=1)),
                       dict(referenced=True), dict(storage_state="COMMITTED"),
                       dict(storage_state="STAGED"), dict(updated_at=self.now)):
            lease = replace(CleanupLease(old, old, "ORPHANED", False), **change)
            self.assertFalse(self.storage.cleanup(staged.storage_key, area="quarantine", lease_guard=guard))
            self.assertTrue(path.exists())
        lease = CleanupLease(old, old, "ORPHANED", False)
        self.assertTrue(self.storage.cleanup(staged.storage_key, area="quarantine", lease_guard=guard))
        self.assertFalse(path.exists())
        self.assertEqual(calls, [staged.storage_key] * 6)

    def test_reconciliation_returns_keys_only_and_never_publishes(self):
        staged = self.stage()
        self.assertEqual(self.storage.reconciliation_candidates(area="quarantine"), ())
        old = self.now - timedelta(hours=2)
        path = self.root / "quarantine" / staged.storage_key
        os.utime(path, (old.timestamp(), old.timestamp()))
        candidates = self.storage.reconciliation_candidates(area="quarantine")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].storage_key, staged.storage_key)
        self.assertNotIn(str(self.root), str(asdict(candidates[0])))
        self.assertTrue(path.exists())
        self.assertEqual(list((self.root / "objects").iterdir()), [])

    def test_cleanup_does_not_race_active_scan(self):
        staged = self.stage()
        old = self.now - timedelta(hours=2)
        path = self.root / "quarantine" / staged.storage_key
        os.utime(path, (old.timestamp(), old.timestamp()))
        calls = []
        @contextmanager
        def guard(key):
            calls.append(key)
            yield CleanupLease(old, old, "ORPHANED", False)
        with self.storage._lock(".scan.lock", 1):
            self.assertFalse(self.storage.cleanup(staged.storage_key, area="quarantine", lease_guard=guard))
        self.assertEqual(calls, [])
        self.assertTrue(path.exists())

    def test_symlink_or_reparse_point_is_not_followed(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_bytes(b"outside")
        key = str(uuid4())
        link = self.root / "objects" / key
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("This Windows account cannot create symlinks")
        with self.assertRaises((StorageUnavailable, StorageIntegrityError)):
            with self.storage.open_verified(key, hashlib.sha256(b"outside").hexdigest(), 7):
                self.fail("Symlink bytes were exposed")
        self.assertEqual(outside.read_bytes(), b"outside")

    def test_errors_never_expose_raw_storage_path(self):
        with self.assertRaises(StorageUnavailable) as caught:
            with self.storage.open_verified(str(uuid4()), "0" * 64, 1):
                pass
        self.assertEqual(str(caught.exception), "STORAGE_UNAVAILABLE")
        self.assertNotIn(str(self.root), repr(caught.exception))


class _SocketDouble:
    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.sent = []
        self.connected = None
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def settimeout(self, value):
        if value <= 0:
            raise AssertionError("Non-positive deadline")
    def connect(self, path):
        if self.error:
            raise self.error
        self.connected = path
    def sendall(self, value):
        self.sent.append(value)
    def recv(self, length):
        reply, self.reply = self.reply, b""
        return reply


class ClamdProtocolTests(unittest.TestCase):
    def setUp(self):
        # This Python Windows build omits AF_UNIX. All sockets in this suite
        # are explicit protocol doubles; no daemon or network is contacted.
        family = patch("vdt.evidence.scanner.socket.AF_UNIX", getattr(socket, "AF_UNIX", 1), create=True)
        family.start()
        self.addCleanup(family.stop)
        self.now = datetime(2026, 10, 23, 12, tzinfo=timezone.utc)
        self.version = b"ClamAV 1.4.3/28000/Fri Oct 23 10:00:00 2026\x00"
        self.scanner = ClamdScanner("/run/clamav/clamd.sock", expected_engine_version="1.4.3",
                                    expected_signature_version="28000", clock=lambda: self.now)

    def test_local_instream_framing_versions_and_no_path_command(self):
        connections = [_SocketDouble(self.version), _SocketDouble(b"stream: OK\x00"), _SocketDouble(self.version)]
        with patch("vdt.evidence.scanner.socket.socket", side_effect=connections) as factory:
            result = self.scanner.scan(io.BytesIO(b"ordinary test bytes"))
        self.assertEqual(result.verdict, ScanVerdict.CLEAN)
        self.assertEqual(connections[1].sent, [b"zINSTREAM\x00", struct.pack(">I", 19) + b"ordinary test bytes", b"\x00" * 4])
        for call in factory.call_args_list:
            self.assertEqual(call.args, (socket.AF_UNIX, socket.SOCK_STREAM))
        self.assertEqual(connections[0].sent, [b"zVERSION\x00"])
        self.assertEqual(connections[2].sent, [b"zVERSION\x00"])

    def test_timeout_and_unavailable_fail_closed(self):
        for error in (TimeoutError("local socket timeout"), ConnectionError("not started")):
            with patch("vdt.evidence.scanner.socket.socket", return_value=_SocketDouble(error=error)):
                with self.assertRaises(ScannerUnavailable):
                    self.scanner.scan(io.BytesIO(b"ordinary"))

    def test_stale_or_changed_versions_fail_closed(self):
        for version in (b"ClamAV 1.4.3/28000/Wed Oct 21 10:00:00 2026\x00",
                        b"ClamAV 1.4.3/28001/Fri Oct 23 10:00:00 2026\x00"):
            with patch("vdt.evidence.scanner.socket.socket", return_value=_SocketDouble(version)):
                with self.assertRaises(ScannerUnavailable):
                    self.scanner.scan(io.BytesIO(b"ordinary"))

    def test_error_partial_or_extra_reply_never_clean(self):
        for reply in (b"stream: size exceeded ERROR\x00", b"stream: OK", b"stream: OK\x00stream: ERROR\x00"):
            connections = [_SocketDouble(self.version), _SocketDouble(reply)]
            with patch("vdt.evidence.scanner.socket.socket", side_effect=connections):
                with self.assertRaises(ScannerUnavailable):
                    self.scanner.scan(io.BytesIO(b"ordinary"))


if __name__ == "__main__":
    unittest.main()
