"""Local PostgreSQL catalog seed checks; never creates people or grants."""
import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import psycopg

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vdt.settings')
import django
django.setup()
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, transaction
from database import parameters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    params = parameters()
    checks = []
    def record(name, passed, detail=None):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    def rows(query):
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    def catalog():
        return {name: rows(f'SELECT * FROM vdt.{name} ORDER BY id') for name in ('permission', 'role', 'role_permission')}
    def domain_counts():
        return {name: rows(f'SELECT count(*) FROM vdt.{name}')[0][0] for name in ('organization', 'app_user', 'role_assignment', 'scope')}
    before_domain = domain_counts()
    before_catalog = catalog()
    first_output = io.StringIO()
    call_command('seed_rbac_catalog', stdout=first_output)
    first = catalog()
    record('Exact catalog cardinality', {k: len(v) for k, v in first.items()} == {'permission': 19, 'role': 4, 'role_permission': 22})
    actual = set(rows('SELECT r.code,p.code FROM vdt.role_permission rp JOIN vdt.role r ON r.id=rp.role_id JOIN vdt.permission p ON p.id=rp.permission_id'))
    required = {('VDT_SECURITY', 'evidence.verify'), ('VDT_SECURITY', 'evidence.read_assigned'),
                ('VDT_REVIEWER', 'evidence.verify'), ('VDT_REVIEWER', 'evidence.read_assigned'),
                ('VDT_RISK_OWNER', 'risk.priority_approve')}
    record('User-required permission mappings present', required <= actual, sorted(required))
    second_output = io.StringIO()
    call_command('seed_rbac_catalog', stdout=second_output)
    record('Repeated seed preserves every catalog row and UUID', catalog() == first)
    record('Seed does not create organizations, users, scope or assignments', domain_counts() == before_domain, before_domain)
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("UPDATE vdt.permission SET description='SYNTHETIC DRIFT CHECK' WHERE code='evidence.verify'")
        try:
            call_command('seed_rbac_catalog', stdout=io.StringIO())
        except CommandError:
            record('Existing catalog drift is refused', True)
        else:
            record('Existing catalog drift is refused', False)
        transaction.set_rollback(True)
    record('Drift check rolls back without changing real catalog', catalog() == first)
    with psycopg.connect(**dict(params, user='vdt_app', password=os.environ['VDT_DB_APP_PASSWORD']), autocommit=True) as app:
        record('Runtime can read permission catalog', app.execute('SELECT count(*) FROM vdt.permission').fetchone()[0] == 19)
        for table in ('permission', 'role', 'role_permission'):
            try:
                with app.transaction():
                    app.execute(f'UPDATE vdt.{table} SET id=id WHERE false')
            except psycopg.Error as error:
                record(f'Runtime cannot mutate {table}', error.sqlstate == '42501', error.sqlstate)
            else:
                record(f'Runtime cannot mutate {table}', False)
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(), 'scope': 'LOCAL_RBAC_CATALOG_ONLY',
        'seed_sha256': hashlib.sha256((ROOT / 'docs/design/rbac-seed-v0.1.json').read_bytes()).hexdigest(),
        'counts_before': {k: len(v) for k, v in before_catalog.items()},
        'counts_after': {k: len(v) for k, v in first.items()}, 'checks': checks,
        'passed': sum(c['passed'] for c in checks), 'failed': sum(not c['passed'] for c in checks),
        'users_provisioned': False, 'role_assignments_created': False, 'CRM_FLOW_TC_VALID_G': 'NOT_RUN',
        'seed_first_stdout': first_output.getvalue(), 'seed_second_stdout': second_output.getvalue(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('counts_before', 'counts_after', 'passed', 'failed')}, indent=2))
    return bool(result['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
