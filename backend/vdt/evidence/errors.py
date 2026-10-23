"""Public-safe errors; never include physical paths or daemon replies."""


class EvidenceError(Exception):
    code = "EVIDENCE_ERROR"
    status_code = 400
    retryable = False

    def __init__(self):
        super().__init__(self.code)


class UploadTooLarge(EvidenceError):
    code = "EVIDENCE_TOO_LARGE"
    status_code = 413


class MetadataTooLarge(UploadTooLarge):
    code = "METADATA_TOO_LARGE"


class InvalidMetadata(EvidenceError):
    code = "INVALID_METADATA"


class InvalidFile(EvidenceError):
    code = "UNSUPPORTED_OR_INVALID_FILE"
    status_code = 415


class HashMismatch(EvidenceError):
    code = "CHECKSUM_MISMATCH"
    status_code = 422


class UnsafeStorageKey(EvidenceError):
    code = "INVALID_STORAGE_KEY"


class StorageUnavailable(EvidenceError):
    code = "STORAGE_UNAVAILABLE"
    status_code = 503
    retryable = True


class StorageIntegrityError(EvidenceError):
    code = "STORAGE_INTEGRITY_FAILED"
    status_code = 409


class ScannerUnavailable(EvidenceError):
    code = "SCANNER_UNAVAILABLE"
    status_code = 503
    retryable = True


class StaleSignatures(ScannerUnavailable):
    code = "SCANNER_SIGNATURES_STALE"


class MalwareDetected(EvidenceError):
    code = "FILE_SCAN_REJECTED"
    status_code = 422
