"""Conservative format checks; uploaded documents are never rendered or executed."""

import csv
import hashlib
import io
import json
import re
import struct
import zlib
from pathlib import PurePosixPath

from .errors import InvalidFile, InvalidMetadata, MetadataTooLarge


ALLOWED_PAIRS = {
    ".txt": "text/plain", ".log": "text/plain", ".json": "application/json",
    ".csv": "text/csv", ".pdf": "application/pdf", ".png": "image/png",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
}


def metadata_digest(metadata, max_bytes):
    try:
        if isinstance(metadata, bytes):
            if len(metadata) > max_bytes:
                raise MetadataTooLarge()
            metadata = json.loads(metadata.decode("utf-8"))
        if not isinstance(metadata, dict):
            raise InvalidMetadata()
        encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise InvalidMetadata() from None
    if len(encoded) > max_bytes:
        raise MetadataTooLarge()
    return hashlib.sha256(encoded).hexdigest()


def safe_extension(filename):
    if (not isinstance(filename, str) or not filename or len(filename) > 255
            or any(c in filename for c in "/\\:")
            or any(ord(c) < 32 or ord(c) == 127 for c in filename)
            or filename in (".", "..")):
        raise InvalidFile()
    return PurePosixPath(filename).suffix.lower()


def _text(data):
    try:
        value = data.decode("utf-8-sig")
    except UnicodeError:
        raise InvalidFile() from None
    if any(ord(c) < 32 and c not in "\t\r\n" for c in value):
        raise InvalidFile()
    prefix = value.lstrip().lower()
    if (re.search(r"<(?:!doctype\s+html|html|script|svg)(?:\s|>|/)", prefix)
            or prefix.startswith("<?xml")
            or data.startswith((b"MZ", b"PK\x03\x04", b"PK\x05\x06", b"\x7fELF", b"%PDF-"))):
        raise InvalidFile()
    return value


def _png(data):
    if len(data) < 45 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise InvalidFile()
    length, chunk = struct.unpack(">I4s", data[8:16])
    if length != 13 or chunk != b"IHDR":
        raise InvalidFile()
    width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", data[16:29])
    allowed_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
    if (not 0 < width <= 16384 or not 0 < height <= 16384 or width * height > 100_000_000
            or depth not in allowed_depths.get(color, set()) or compression != 0
            or filtering != 0 or interlace not in (0, 1)
            or zlib.crc32(data[12:29]) & 0xffffffff != struct.unpack(">I", data[29:33])[0]):
        raise InvalidFile()
    offset, saw_idat, saw_iend = 33, False, False
    while offset + 12 <= len(data):
        length, chunk = struct.unpack(">I4s", data[offset:offset + 8])
        end = offset + 12 + length
        if end > len(data) or chunk == b"IHDR":
            raise InvalidFile()
        if zlib.crc32(data[offset + 4:end - 4]) & 0xffffffff != struct.unpack(">I", data[end - 4:end])[0]:
            raise InvalidFile()
        saw_idat |= chunk == b"IDAT"
        if chunk == b"IEND":
            saw_iend = length == 0 and end == len(data)
            break
        offset = end
    if not saw_idat or not saw_iend:
        raise InvalidFile()


def _jpeg(data):
    if not data.startswith(b"\xff\xd8\xff") or not data.endswith(b"\xff\xd9"):
        raise InvalidFile()
    offset, saw_frame = 2, False
    while offset < min(len(data) - 2, 1_048_576):
        if data[offset] != 0xff:
            raise InvalidFile()
        while offset < len(data) and data[offset] == 0xff:
            offset += 1
        if offset >= len(data):
            raise InvalidFile()
        marker = data[offset]
        offset += 1
        if marker in (0, 0xd8, 0xd9) or 0xd0 <= marker <= 0xd7 or offset + 2 > len(data):
            raise InvalidFile()
        length = struct.unpack(">H", data[offset:offset + 2])[0]
        if length < 2 or offset + length > len(data):
            raise InvalidFile()
        if marker in (0xc0, 0xc1, 0xc2):
            if length < 11:
                raise InvalidFile()
            precision, height, width, components = struct.unpack(">BHHB", data[offset + 2:offset + 8])
            if (precision != 8 or components not in (1, 3, 4) or length != 8 + components * 3
                    or not 0 < width <= 16384 or not 0 < height <= 16384 or width * height > 100_000_000):
                raise InvalidFile()
            saw_frame = True
        if marker == 0xda:
            if not saw_frame or length < 6:
                raise InvalidFile()
            return
        offset += length
    raise InvalidFile()


def _pdf(data):
    if not re.match(br"%PDF-[12]\.[0-9]", data) or not data.rstrip().endswith(b"%%EOF"):
        raise InvalidFile()
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data), strict=True)
        if reader.is_encrypted or not 0 < len(reader.pages) <= 10000:
            raise InvalidFile()
        for page in reader.pages:
            if page.get("/Type") != "/Page" or len(page.mediabox) != 4:
                raise InvalidFile()
        if "/Root" not in reader.trailer:
            raise InvalidFile()
    except InvalidFile:
        raise
    except Exception:
        raise InvalidFile() from None


def validate_file(handle, filename, declared_mime, allowed_pairs, max_bytes):
    extension = safe_extension(filename)
    mime = allowed_pairs.get(extension)
    if mime is None or ALLOWED_PAIRS.get(extension) != mime:
        raise InvalidFile()
    declaration = (declared_mime or "").split(";", 1)[0].strip().lower()
    if declaration and declaration not in (mime, "application/octet-stream"):
        if not (mime == "text/csv" and declaration == "text/plain"):
            raise InvalidFile()
    handle.seek(0)
    data = handle.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise InvalidFile()
    try:
        if mime in ("text/plain", "text/csv", "application/json"):
            value = _text(data)
            if mime == "application/json":
                json.loads(value, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            elif mime == "text/csv":
                for _ in csv.reader(io.StringIO(value, newline=""), strict=True):
                    pass
        elif mime == "image/png":
            _png(data)
        elif mime == "image/jpeg":
            _jpeg(data)
        elif mime == "application/pdf":
            _pdf(data)
        else:
            raise InvalidFile()
    except (ValueError, UnicodeError, csv.Error, RecursionError):
        raise InvalidFile() from None
    finally:
        handle.seek(0)
    return mime
