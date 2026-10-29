"""Closed request schemas from the frozen contract, with canonical identifiers."""
from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata
from uuid import UUID

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
import yaml

from vdt.authn.service import AuthError


def fail(code, status, detail):
    raise AuthError(code, status, detail)


def uuid_text(value):
    try:
        parsed = str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        fail('INVALID_INPUT', 422, 'Định danh không hợp lệ.')
    if parsed != value:
        fail('INVALID_INPUT', 422, 'Định danh phải ở dạng UUID chuẩn.')
    return parsed


@lru_cache(maxsize=1)
def contract():
    doc = yaml.safe_load((Path(settings.BASE_DIR) / 'docs/design/openapi-v0.1.yaml').read_text(encoding='utf-8'))
    # OpenAPI's components are valid local reference targets in this JSON Schema resource.
    resource = Resource.from_contents(dict(doc, **{'$schema':'https://json-schema.org/draft/2020-12/schema'}))
    return doc, Registry().with_resource('urn:vdt:contract', resource)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key')
        result[key] = value
    return result


@lru_cache(maxsize=32)
def schema_validator(schema_name):
    _, registry = contract()
    return Draft202012Validator({'$ref':f'urn:vdt:contract#/components/schemas/{schema_name}'},
                                registry=registry, format_checker=FormatChecker())


def payload(request, schema_name, *, validator=None):
    if request.content_type != 'application/json':
        fail('UNSUPPORTED_MEDIA_TYPE', 415, 'Yêu cầu phải dùng JSON.')
    if len(request.body) > 64 * 1024:
        fail('PAYLOAD_TOO_LARGE', 413, 'Yêu cầu quá lớn.')
    try:
        value = json.loads(request.body.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, RecursionError):
        fail('INVALID_JSON', 400, 'Nội dung JSON không hợp lệ.')
    if not (validator or schema_validator(schema_name)).is_valid(value):
        fail('INVALID_INPUT', 422, 'Các trường yêu cầu không hợp lệ.')
    def inspect(node, key=''):
        if isinstance(node, dict):
            for child_key, child in node.items():
                inspect(child, child_key)
        elif isinstance(node, list):
            if key.endswith('_ids'):
                if len(set(node)) != len(node):
                    fail('INVALID_INPUT', 422, 'Danh sách định danh bị trùng.')
                for item in node:
                    uuid_text(item)
            for child in node:
                inspect(child)
        elif isinstance(node, str):
            if '\x00' in node:
                fail('INVALID_INPUT', 422, 'Nội dung chứa ký tự không hợp lệ.')
            if key == 'id' or key.endswith('_id'):
                uuid_text(node)
    inspect(value)
    return value


def clean_text(value, maximum=4000):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or len(value)>maximum:
        fail('INVALID_INPUT', 422, 'Nội dung không được để trống hoặc có khoảng trắng ở đầu/cuối.')
    if any(unicodedata.category(c).startswith('C') for c in value):
        fail('INVALID_INPUT', 422, 'Nội dung chứa ký tự điều khiển.')
    return value


def username(value):
    value = unicodedata.normalize('NFKC', value)
    clean_text(value, 150)
    try:
        UnicodeUsernameValidator()(value)
    except ValidationError:
        fail('INVALID_INPUT', 422, 'Tên đăng nhập không hợp lệ.')
    return value


def timestamp(value):
    parsed = parse_datetime(value)
    if parsed is None or parsed.utcoffset() is None:
        fail('INVALID_INPUT', 422, 'Thời điểm cần có múi giờ.')
    return parsed


def expected_version(request, required=False):
    value = request.headers.get('If-Match')
    if value is None:
        if required:
            fail('PRECONDITION_REQUIRED', 428, 'Cần đọc lại tài nguyên trước khi thay đổi.')
        return None
    if not re.fullmatch(r'"[1-9][0-9]{0,17}"', value):
        fail('INVALID_HEADER', 400, 'If-Match không hợp lệ.')
    return int(value[1:-1])


def assert_version(actual, expected):
    if actual != expected:
        fail('ETAG_MISMATCH', 412, 'Dữ liệu đã thay đổi. Hãy tải lại trước khi lưu.')
