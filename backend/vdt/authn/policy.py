"""Explicit VDT development policy; never an AUTH-CRM-01 configuration."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import ipaddress
import unicodedata
from urllib.parse import urlsplit


@dataclass(frozen=True)
class AuthPolicy:
    profile: str
    idle_timeout_seconds: int
    absolute_timeout_seconds: int
    max_attempts: int
    attempt_window_seconds: int
    lockout_seconds: int

    @classmethod
    def from_mapping(cls, value):
        if not isinstance(value, dict) or set(value) != set(cls.__dataclass_fields__):
            raise ValueError('VDT_AUTH_POLICY must contain exactly the documented fields.')
        if value['profile'] != 'DEVELOPMENT_LOCAL':
            raise ValueError('Only the explicit DEVELOPMENT_LOCAL profile is implemented.')
        limits = {'idle_timeout_seconds': (60, 86400), 'absolute_timeout_seconds': (60, 604800),
                  'max_attempts': (1, 20), 'attempt_window_seconds': (60, 86400),
                  'lockout_seconds': (60, 86400)}
        for key, (low, high) in limits.items():
            if type(value[key]) is not int or not low <= value[key] <= high:
                raise ValueError(f'Invalid {key}.')
        if value['idle_timeout_seconds'] > value['absolute_timeout_seconds']:
            raise ValueError('Idle lifetime must not exceed absolute lifetime.')
        return cls(**value)

    def idle_expiry(self, last_seen, absolute_expiry):
        return min(last_seen + timedelta(seconds=self.idle_timeout_seconds), absolute_expiry)

    def is_live(self, *, now, last_seen, absolute_expiry, revoked_at, active):
        timestamps = (now, last_seen, absolute_expiry)
        return (active is True and revoked_at is None
                and all(isinstance(t, datetime) and t.utcoffset() is not None for t in timestamps)
                and last_seen <= now < self.idle_expiry(last_seen, absolute_expiry))


def literal_ip(value):
    if not isinstance(value, str) or len(value) > 45 or '%' in value:
        raise ValueError('One literal proxy-observed client IP is required.')
    return str(ipaddress.ip_address(value))


def normalize_username(value):
    if not isinstance(value, str):
        raise ValueError('Username must be text.')
    normalized = unicodedata.normalize('NFKC', value).strip()
    if not normalized or len(normalized) > 150 or '\x00' in normalized:
        raise ValueError('Username is empty or exceeds its limit.')
    return normalized


def validate_origins(value):
    if not isinstance(value, (tuple, list)) or not value:
        raise ValueError('Explicit HTTPS VDT origins are required.')
    origins = set()
    for origin in value:
        if not isinstance(origin, str):
            raise ValueError('Invalid origin.')
        parsed = urlsplit(origin)
        if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.path or parsed.query or parsed.fragment or '*' in origin):
            raise ValueError('Origins must be exact HTTPS origins without paths or credentials.')
        _ = parsed.port
        origins.add(origin)
    return frozenset(origins)
