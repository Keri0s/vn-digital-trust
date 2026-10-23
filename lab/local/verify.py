"""Run the isolated unit suite and save factual, non-secret verification results."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
from vdt.configuration import load_configuration, preflight


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_ids.append(test.id())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests/unit'))
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    source_paths = list((ROOT / 'backend').rglob('*.py')) + list((ROOT / 'tests').rglob('*.py'))
    source_paths += list((ROOT / 'lab/local').glob('*.py'))
    source_paths += [ROOT / 'backend/requirements.lock', ROOT / 'backend/vdt/core/migrations/0001_domain.sql',
                     ROOT / 'docs/design/openapi-v0.1.yaml', ROOT / 'docs/design/config-template-v0.1.json']
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_paths)}
    crm = preflight(load_configuration(ROOT / 'docs/design/config-template-v0.1.json'), target='crm').as_dict()
    document = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'ISOLATED_FOUNDATION_MODULES_AND_IN_PROCESS_HTTP_ONLY',
        'python': platform.python_version(), 'platform': platform.platform(),
        'packages': {name: version(name) for name in ('Django', 'djangorestframework', 'psycopg', 'pypdf')},
        'tests_run': result.testsRun, 'passed': len(result.passed_ids),
        'failures': [test.id() for test, _ in result.failures],
        'errors': [test.id() for test, _ in result.errors],
        'skipped': [{'test': test.id(), 'reason': reason} for test, reason in result.skipped],
        'successful': result.wasSuccessful(), 'passed_ids': result.passed_ids,
        'crm_template_preflight': crm, 'FLOW_TC_VALID_G': 'NOT_RUN',
        'source_sha256': hashes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
