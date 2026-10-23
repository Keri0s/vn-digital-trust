"""Bootstrap/check the dedicated local foundation database, never a CRM database."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]


def parameters():
    if os.environ.get('VDT_LOCAL_FOUNDATION_ONLY') != 'true' or os.environ.get('PGDATABASE') != 'vdt_step06':
        raise SystemExit('Refused: explicit local foundation database configuration required.')
    return dict(host=os.environ['PGHOST'], port=os.environ.get('PGPORT', '5432'),
                dbname='vdt_step06', user=os.environ['PGUSER'], password=os.environ['PGPASSWORD'])


def migrate(params):
    subprocess.run([sys.executable, str(ROOT / 'backend/manage.py'), 'migrate', '--noinput'], check=True)
    with psycopg.connect(**params, autocommit=True) as connection:
        if not connection.execute("SELECT 1 FROM pg_roles WHERE rolname='vdt_app'").fetchone():
            connection.execute('CREATE ROLE vdt_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT')
        connection.execute(sql.SQL('ALTER ROLE vdt_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT PASSWORD {}').format(sql.Literal(os.environ['VDT_DB_APP_PASSWORD'])))
        for statement in (
            'GRANT CONNECT ON DATABASE vdt_step06 TO vdt_app',
            'GRANT USAGE ON SCHEMA vdt,public TO vdt_app',
            'GRANT SELECT,INSERT,UPDATE ON ALL TABLES IN SCHEMA vdt TO vdt_app',
            'REVOKE INSERT,UPDATE ON vdt.permission,vdt.role,vdt.role_permission FROM vdt_app',
            'GRANT SELECT,INSERT,UPDATE,DELETE ON public.django_session TO vdt_app',
            'REVOKE ALL ON ALL FUNCTIONS IN SCHEMA vdt FROM PUBLIC',
            'GRANT EXECUTE ON FUNCTION vdt.acquire_authorization_guard(uuid) TO vdt_app',
            'REVOKE CREATE ON SCHEMA public FROM PUBLIC',
        ):
            connection.execute(statement)
    print('Local migration and restricted runtime grants applied; no users or CRM data seeded.')


def check(params):
    checks = []
    def record(name, ok, detail=''):
        checks.append({'check': name, 'passed': bool(ok), 'detail': detail})

    with psycopg.connect(**params, autocommit=True) as connection:
        record('PostgreSQL major 17', connection.execute('SHOW server_version_num').fetchone()[0].startswith('17'),
               connection.execute('SELECT version()').fetchone()[0])
        count = connection.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='vdt' AND table_type='BASE TABLE'").fetchone()[0]
        record('Domain migration creates 106 tables', count == 106, count)
        original_count = connection.execute('SELECT count(*) FROM vdt.organization').fetchone()[0]
        with connection.transaction():
            org, actor, scope = uuid4(), uuid4(), uuid4()
            connection.execute('INSERT INTO vdt.organization(id,code,name) VALUES (%s,%s,%s)',
                               (org, f'SYNTHETIC-{org}', 'Rollback check only'))
            connection.execute('INSERT INTO vdt.app_user(id,organization_id,login_name,display_name,status) VALUES (%s,%s,%s,%s,%s)',
                               (actor, org, f'synthetic-{actor}', 'Synthetic', 'PENDING'))
            connection.execute("INSERT INTO vdt.scope(id,organization_id,scope_kind,description,content_hash) VALUES (%s,%s,'ORGANIZATION','Synthetic scope',%s)", (scope, org, '0'*64))
            def denied(name, query, arguments, state):
                try:
                    with connection.transaction():
                        connection.execute(query, arguments)
                except psycopg.Error as error:
                    record(name, error.sqlstate == state, {'sqlstate': error.sqlstate})
                else:
                    record(name, False, 'Unexpectedly allowed')
            denied('Scope history UPDATE denied', "UPDATE vdt.scope SET description='changed' WHERE id=%s", (scope,), '55000')
            denied('Scope history DELETE denied', 'DELETE FROM vdt.scope WHERE id=%s', (scope,), '55000')
            denied('Mutable version cannot skip expected increment', 'UPDATE vdt.organization SET version=version+2 WHERE id=%s', (org,), '40001')
            connection.execute('UPDATE vdt.organization SET version=version+1 WHERE id=%s', (org,))
            record('Mutable exact version increment allowed', connection.execute('SELECT version FROM vdt.organization WHERE id=%s', (org,)).fetchone()[0] == 2)
            sid = uuid4()
            try:
                with connection.transaction():
                    connection.execute("INSERT INTO vdt.snapshot_registry(id,snapshot_kind,scope_id,created_by,created_at,content_hash,lineage_id) VALUES (%s,'CONTEXT',%s,%s,now(),%s,%s)", (sid, scope, actor, '0'*64, sid))
                    connection.execute('SET CONSTRAINTS ALL IMMEDIATE')
            except psycopg.Error as error:
                record('Snapshot without payload denied at deferred check', error.sqlstate == '23514', error.sqlstate)
            else:
                record('Snapshot without payload denied at deferred check', False)
            sid = uuid4()
            with connection.transaction():
                connection.execute("INSERT INTO vdt.snapshot_registry(id,snapshot_kind,scope_id,created_by,created_at,content_hash,lineage_id,created_txid) VALUES (%s,'CONTEXT',%s,%s,'2000-01-01',%s,%s,0)", (sid, scope, actor, '0'*64, sid))
                connection.execute("INSERT INTO vdt.context_snapshot(id,schema_version,facts,preconditions,input_versions) VALUES (%s,'v0.1','{}','{}','{}')", (sid,))
                connection.execute('SET CONSTRAINTS ALL IMMEDIATE')
                row = connection.execute("SELECT created_txid=txid_current(),created_at>now()-interval '1 minute' FROM vdt.snapshot_registry WHERE id=%s", (sid,)).fetchone()
                record('Snapshot transaction/time stamped by server', all(row))
            denied('Snapshot immutable payload UPDATE denied', "UPDATE vdt.context_snapshot SET facts='{}' WHERE id=%s", (sid,), '55000')
            raise psycopg.Rollback()
        with psycopg.connect(**dict(params, user='vdt_app', password=os.environ['VDT_DB_APP_PASSWORD']), autocommit=True) as app:
            rights = app.execute('SELECT rolsuper,rolcreaterole,rolcreatedb FROM pg_roles WHERE rolname=current_user').fetchone()
            record('Runtime DB role has no administrative privileges', not any(rights))
            for name, query in (
                ('Runtime cannot TRUNCATE immutable history', "SELECT has_table_privilege(current_user,'vdt.scope','TRUNCATE')"),
                ('Runtime cannot DELETE immutable history', "SELECT has_table_privilege(current_user,'vdt.scope','DELETE')"),
                ('Runtime cannot CREATE in domain schema', "SELECT has_schema_privilege(current_user,'vdt','CREATE')"),
            ):
                record(name, not app.execute(query).fetchone()[0])
            try:
                with app.transaction():
                    app.execute('ALTER TABLE vdt.scope DISABLE TRIGGER USER')
            except psycopg.Error as error:
                record('Runtime cannot disable history triggers', error.sqlstate == '42501', error.sqlstate)
            else:
                record('Runtime cannot disable history triggers', False)
        record('Synthetic checks preserve organization count', connection.execute('SELECT count(*) FROM vdt.organization').fetchone()[0] == original_count)
    return {'recorded_at': datetime.now(timezone.utc).isoformat(), 'scope': 'POSTGRESQL_17_FOUNDATION_ONLY',
            'CRM_FLOW_TC_VALID_G': 'NOT_RUN', 'checks': checks, 'passed': sum(c['passed'] for c in checks),
            'failed': sum(not c['passed'] for c in checks)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('migrate', 'check'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    params = parameters()
    if args.action == 'migrate':
        migrate(params)
        return 0
    result = check(params)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding='utf-8')
    print(serialized)
    return bool(result['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
