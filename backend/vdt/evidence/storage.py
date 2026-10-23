"""Private local bytes, independent of database and business verification.

Caller sequence: authorize -> stage -> scan -> persist DB STAGED with final key
-> promote -> short, reauthorized DB COMMITTED transaction. Physical promotion
does not publish bytes or mark a revision verified. Final-transaction failure
leaves a recoverable object; reconciliation must never commit it automatically.
"""

import ctypes
import hashlib
import hmac
import os
import re
import shutil
import stat
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, ContextManager
from uuid import UUID, uuid4

from .errors import (EvidenceError, HashMismatch, MalwareDetected, ScannerUnavailable,
                     StaleSignatures, StorageIntegrityError, StorageUnavailable,
                     UnsafeStorageKey, UploadTooLarge)
from .formats import ALLOWED_PAIRS, metadata_digest, safe_extension, validate_file
from .scanner import ScanResult, ScanVerdict


@dataclass(frozen=True)
class EvidenceLimits:
    max_file_bytes: int = 20 * 1024 * 1024
    max_metadata_bytes: int = 64 * 1024
    max_staging_bytes: int = 100 * 1024 * 1024
    minimum_free_disk_bytes: int = 2 * 1024 * 1024 * 1024
    staging_orphan_grace_seconds: int = 3600
    upload_read_timeout_seconds: int = 120
    scan_timeout_seconds: int = 60
    signature_max_age_seconds: int = 86400
    allowed_pairs: dict = field(default_factory=lambda: dict(ALLOWED_PAIRS))

    def __post_init__(self):
        if (not 0 < self.max_file_bytes <= 20 * 1024 * 1024
                or not 0 < self.max_metadata_bytes <= 64 * 1024
                or self.max_staging_bytes < self.max_file_bytes
                or self.minimum_free_disk_bytes < 0 or self.staging_orphan_grace_seconds < 0
                or min(self.upload_read_timeout_seconds, self.scan_timeout_seconds,
                       self.signature_max_age_seconds) <= 0
                or not self.allowed_pairs
                or any(ALLOWED_PAIRS.get(k) != v for k, v in self.allowed_pairs.items())):
            raise ValueError("Invalid evidence policy")

    @classmethod
    def from_config(cls, config):
        evidence = config["vdt"]["evidence"]
        scanner = config["vdt"]["scanner"]
        values = {name: evidence[name] for name in (
            "max_file_bytes", "max_metadata_bytes", "max_staging_bytes",
            "minimum_free_disk_bytes", "staging_orphan_grace_seconds",
            "upload_read_timeout_seconds", "scan_timeout_seconds")}
        values["allowed_pairs"] = {extension: entry["mime"]
                                    for entry in evidence["allowed_extension_mime_pairs"]
                                    for extension in entry["extensions"]}
        values["signature_max_age_seconds"] = scanner["signature_max_age_seconds"]
        return cls(**values)


@dataclass(frozen=True)
class StagedBlob:
    storage_key: str
    operation_id: str
    sha256: str
    size_bytes: int
    mime: str
    metadata_sha256: str


@dataclass(frozen=True)
class ScannedBlob(StagedBlob):
    scan_result: ScanResult
    _proof: object = field(repr=False, compare=False)


@dataclass(frozen=True)
class StoredBlob(StagedBlob):
    scan_result: ScanResult


@dataclass(frozen=True)
class CleanupLease:
    """Must be read under the caller's durable operation/fencing lock.

    The caller prevents renewals/publication while the context is open, validates
    its fencing token, and commits an audit/storage event after a True result.
    MISSING means an explicitly confirmed absence of any owning DB operation.
    """
    lease_expires_at: datetime
    updated_at: datetime
    storage_state: str
    referenced: bool


@dataclass(frozen=True)
class ReconciliationCandidate:
    storage_key: str
    area: str
    size_bytes: int
    modified_at: datetime


def _key(value):
    if not isinstance(value, str):
        raise UnsafeStorageKey()
    try:
        parsed = UUID(value)
    except ValueError:
        raise UnsafeStorageKey() from None
    if str(parsed) != value or parsed.version != 4:
        raise UnsafeStorageKey()
    return value


def _reparse(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


class LocalEvidenceStorage:
    def __init__(self, root, limits=None, *, clock=None):
        self.limits = limits or EvidenceLimits()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._root = Path(root)
        self._proofs = {}
        if not self._root.is_absolute():
            raise StorageUnavailable()
        try:
            for parent in reversed((self._root, *self._root.parents)):
                if parent.exists() and _reparse(parent.lstat()):
                    raise StorageUnavailable()
            self._root.mkdir(mode=0o700, parents=True, exist_ok=True)
            self._identities = {}
            for name in ("", "quarantine", "objects"):
                directory = self._root / name
                directory.mkdir(mode=0o700, exist_ok=True)
                info = directory.lstat()
                if _reparse(info) or not stat.S_ISDIR(info.st_mode):
                    raise StorageUnavailable()
                if os.name == "posix" and info.st_mode & 0o077:
                    raise StorageUnavailable()
                self._identities[name] = (info.st_dev, info.st_ino)
            if self._identities["quarantine"][0] != self._identities["objects"][0]:
                raise StorageUnavailable()
        except OSError:
            raise StorageUnavailable() from None

    def _check_directory(self, area):
        if area not in self._identities:
            raise StorageUnavailable()
        for parent in self._root.parents:
            if _reparse(parent.lstat()):
                raise StorageUnavailable()
        for name in ("", area):
            info = (self._root / name).lstat()
            if (_reparse(info) or (info.st_dev, info.st_ino) != self._identities[name]
                    or (os.name == "posix" and info.st_mode & 0o077)):
                raise StorageUnavailable()

    @contextmanager
    def _directory(self, area):
        self._check_directory(area)
        descriptor = None
        root_descriptor = None
        try:
            if os.name == "posix":
                flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                root_descriptor = os.open(self._root, flags)
                descriptor = os.open(area or ".", flags, dir_fd=root_descriptor)
                info = os.fstat(descriptor)
                if (info.st_dev, info.st_ino) != self._identities[area]:
                    raise StorageUnavailable()
            yield descriptor
        finally:
            if descriptor is not None:
                os.close(descriptor)
            if root_descriptor is not None:
                os.close(root_descriptor)

    def _open(self, area, key, flags, *, internal=False):
        if not internal:
            _key(key)
        try:
            with self._directory(area) as directory:
                if directory is not None:
                    descriptor = os.open(key, flags | os.O_NOFOLLOW, 0o600, dir_fd=directory)
                else:
                    path = self._root / area / key
                    if path.exists() and _reparse(path.lstat()):
                        raise StorageIntegrityError()
                    descriptor = os.open(path, flags | getattr(os, "O_BINARY", 0), 0o600)
                try:
                    info = os.fstat(descriptor)
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                        raise StorageIntegrityError()
                    if directory is None:
                        after = (self._root / area / key).lstat()
                        if _reparse(after) or (info.st_dev, info.st_ino) != (after.st_dev, after.st_ino):
                            raise StorageIntegrityError()
                    return os.fdopen(descriptor, "r+b" if flags & os.O_RDWR else "rb")
                except BaseException:
                    os.close(descriptor)
                    raise
        except OSError:
            raise StorageUnavailable() from None

    def _sync_directory(self, area):
        with self._directory(area) as descriptor:
            if descriptor is not None:
                os.fsync(descriptor)

    def _unlink(self, area, key):
        _key(key)
        with self._directory(area) as descriptor:
            if descriptor is not None:
                os.unlink(key, dir_fd=descriptor)
            else:
                os.unlink(self._root / area / key)
        self._sync_directory(area)

    @contextmanager
    def _lock(self, name, timeout):
        # OS advisory locks are released on process death; they do not replace
        # the database operation lease/fencing and principal upload quotas.
        with self._open("", name, os.O_RDWR | os.O_CREAT, internal=True) as handle:
            if os.name == "nt":
                import msvcrt
                if os.fstat(handle.fileno()).st_size == 0:
                    handle.write(b"0")
                    handle.flush()
                acquire = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                release = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                acquire = lambda: fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                release = lambda: fcntl.flock(handle, fcntl.LOCK_UN)
            deadline = time.monotonic() + timeout
            while True:
                handle.seek(0)
                try:
                    acquire()
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise StorageUnavailable() from None
                    time.sleep(0.02)
            try:
                yield
            finally:
                handle.seek(0)
                release()

    def stage(self, chunks, *, filename, declared_mime, metadata,
              expected_sha256=None, operation_id=None):
        """Stream only after authorization; request/multipart caps belong upstream."""
        safe_extension(filename)
        metadata_sha256 = metadata_digest(metadata, self.limits.max_metadata_bytes)
        if expected_sha256 is not None and not re.fullmatch("[0-9a-fA-F]{64}", expected_sha256):
            raise HashMismatch()
        operation_id = _key(operation_id or str(uuid4()))
        key = str(uuid4())
        created = False
        try:
            with self._lock(".quota.lock", self.limits.upload_read_timeout_seconds):
                self._check_directory("quarantine")
                staged_size = sum(p.stat(follow_symlinks=False).st_size
                                  for p in (self._root / "quarantine").iterdir())
                if (staged_size + self.limits.max_file_bytes > self.limits.max_staging_bytes
                        or shutil.disk_usage(self._root).free - self.limits.max_file_bytes
                        < self.limits.minimum_free_disk_bytes):
                    raise StorageUnavailable()
                digest, size = hashlib.sha256(), 0
                deadline = time.monotonic() + self.limits.upload_read_timeout_seconds
                with self._open("quarantine", key, os.O_RDWR | os.O_CREAT | os.O_EXCL) as handle:
                    created = True
                    for chunk in chunks:
                        if time.monotonic() >= deadline:
                            raise StorageUnavailable()
                        if not isinstance(chunk, bytes):
                            raise StorageIntegrityError()
                        size += len(chunk)
                        if size > self.limits.max_file_bytes:
                            raise UploadTooLarge()
                        digest.update(chunk)
                        handle.write(chunk)
                    handle.flush()
                    actual_hash = digest.hexdigest()
                    if expected_sha256 is not None and not hmac.compare_digest(actual_hash, expected_sha256.lower()):
                        raise HashMismatch()
                    mime = validate_file(handle, filename, declared_mime,
                                         self.limits.allowed_pairs, self.limits.max_file_bytes)
                    os.fsync(handle.fileno())
                self._sync_directory("quarantine")
                return StagedBlob(key, operation_id, actual_hash, size, mime, metadata_sha256)
        except BaseException as error:
            if created:
                try:
                    self._unlink("quarantine", key)
                except (EvidenceError, OSError):
                    pass  # Grace/lease-aware reconciliation handles an interrupted delete.
            if isinstance(error, OSError):
                raise StorageUnavailable() from None
            raise

    def _verify(self, handle, digest, size):
        if (not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest)
                or not 0 < size <= self.limits.max_file_bytes):
            raise StorageIntegrityError()
        actual, count = hashlib.sha256(), 0
        handle.seek(0)
        while True:
            chunk = handle.read(64 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > size:
                raise StorageIntegrityError()
            actual.update(chunk)
        if count != size or not hmac.compare_digest(actual.hexdigest(), digest):
            raise StorageIntegrityError()
        handle.seek(0)

    def scan(self, blob, scanner):
        if scanner is None:
            raise ScannerUnavailable()
        with self._lock(".scan.lock", self.limits.scan_timeout_seconds):
            with self._open("quarantine", blob.storage_key, os.O_RDONLY) as handle:
                self._verify(handle, blob.sha256, blob.size_bytes)
                try:
                    result = scanner.scan(handle)
                except EvidenceError:
                    raise
                except Exception:
                    raise ScannerUnavailable() from None
                self._verify(handle, blob.sha256, blob.size_bytes)
            if not isinstance(result, ScanResult):
                raise ScannerUnavailable()
            if not result.valid_at(self._clock(), self.limits.signature_max_age_seconds):
                raise StaleSignatures()
            if result.verdict is not ScanVerdict.CLEAN:
                raise MalwareDetected()
            proof = object()
            self._proofs[blob.storage_key] = proof
            return ScannedBlob(**blob.__dict__, scan_result=result, _proof=proof)

    def _rename_exclusive(self, key):
        with self._directory("quarantine") as source_dir, self._directory("objects") as target_dir:
            if sys.platform.startswith("linux"):
                library = ctypes.CDLL(None, use_errno=True)
                rename = getattr(library, "renameat2", None)
                if rename is None:
                    raise StorageUnavailable()
                rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
                rename.restype = ctypes.c_int
                if rename(source_dir, key.encode("ascii"), target_dir, key.encode("ascii"), 1) != 0:
                    raise StorageUnavailable()
            elif os.name == "nt":
                # No REPLACE_EXISTING: a UUID collision never overwrites an object.
                move = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
                move.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
                move.restype = ctypes.c_int
                if not move(str(self._root / "quarantine" / key), str(self._root / "objects" / key), 8):
                    raise StorageUnavailable()
            else:
                raise StorageUnavailable()  # No unsafe overwrite-capable fallback.

    def promote(self, blob):
        """Persist the expected final key in DB STAGED before calling this method."""
        if not isinstance(blob, ScannedBlob) or self._proofs.get(blob.storage_key) is not blob._proof:
            raise ScannerUnavailable()
        if not blob.scan_result.valid_at(self._clock(), self.limits.signature_max_age_seconds):
            raise StaleSignatures()
        try:
            with self._open("quarantine", blob.storage_key, os.O_RDWR) as handle:
                self._verify(handle, blob.sha256, blob.size_bytes)
                os.fsync(handle.fileno())
            self._rename_exclusive(blob.storage_key)
            self._sync_directory("quarantine")
            self._sync_directory("objects")
            self._proofs.pop(blob.storage_key, None)
            values = {k: v for k, v in blob.__dict__.items() if k != "_proof"}
            return StoredBlob(**values)
        except OSError:
            raise StorageUnavailable() from None

    @contextmanager
    def open_verified(self, storage_key, sha256, size_bytes):
        """Caller gates DB COMMITTED + current scope before entry and during streaming."""
        with self._open("objects", storage_key, os.O_RDONLY) as handle:
            self._verify(handle, sha256, size_bytes)
            yield handle

    def reconciliation_candidates(self, *, area):
        """Return old server keys only; this read never deletes or publishes."""
        if area not in ("quarantine", "objects"):
            raise UnsafeStorageKey()
        try:
            self._check_directory(area)
            now = self._clock()
            result = []
            for entry in (self._root / area).iterdir():
                try:
                    _key(entry.name)
                    info = entry.lstat()
                    if (_reparse(info) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                            or now.timestamp() - info.st_mtime < self.limits.staging_orphan_grace_seconds):
                        continue
                    result.append(ReconciliationCandidate(entry.name, area, info.st_size,
                                  datetime.fromtimestamp(info.st_mtime, timezone.utc)))
                except (UnsafeStorageKey, FileNotFoundError):
                    continue
            return tuple(result)
        except OSError:
            raise StorageUnavailable() from None

    def cleanup(self, storage_key, *, area, lease_guard: Callable[[str], ContextManager[CleanupLease]]):
        """Delete only confirmed orphan bytes under a durable lease/fencing guard.

        No reference/COMMITTED auto-GC; no automatic publication after a crash.
        The guard must encompass database audit and exclusion of active workers.
        """
        _key(storage_key)
        if area not in ("quarantine", "objects"):
            raise UnsafeStorageKey()
        # Refuse cleanup while a stream or scan is currently active. These OS
        # guards supplement, and never replace, the durable fencing callback.
        try:
            with self._lock(".quota.lock", 0), self._lock(".scan.lock", 0):
                return self._cleanup_locked(storage_key, area, lease_guard)
        except StorageUnavailable:
            return False

    def _cleanup_locked(self, storage_key, area, lease_guard):
        with lease_guard(storage_key) as lease:
            now = self._clock()
            if (not isinstance(lease, CleanupLease) or lease.referenced
                    or lease.storage_state not in ("ORPHANED", "MISSING")
                    or now <= lease.lease_expires_at
                    or (now - lease.updated_at).total_seconds() < self.limits.staging_orphan_grace_seconds):
                return False
            try:
                with self._open(area, storage_key, os.O_RDONLY) as handle:
                    age = now.timestamp() - os.fstat(handle.fileno()).st_mtime
                    if age < self.limits.staging_orphan_grace_seconds:
                        return False
                self._unlink(area, storage_key)
                self._proofs.pop(storage_key, None)
                return True
            except (OSError, StorageUnavailable):
                return False
