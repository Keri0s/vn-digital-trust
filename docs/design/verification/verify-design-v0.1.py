"""Read-only design checks. Does not start a DB/app, execute DDL, or run CRM tests."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote
import yaml
from pglast import parser
from openapi_spec_validator import validate_spec
from jsonschema import Draft202012Validator, RefResolver

ap = argparse.ArgumentParser()
ap.add_argument('--design-dir', type=Path, default=Path(__file__).resolve().parents[1])
ap.add_argument('--output', type=Path)
args = ap.parse_args()
base = args.design_dir.resolve()
checks = []

def check(name, condition, detail):
    checks.append({'check': name, 'passed': bool(condition), 'detail': detail})

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name):
    return json.loads((base / name).read_text(encoding='utf-8-sig'))

class UniqueLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node, deep=False):
    pairs = loader.construct_pairs(node, deep=deep)
    data = {}
    for k, v in pairs:
        if k in data:
            raise ValueError(f'Duplicate YAML key: {k}')
        data[k] = v
    return data

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def walk(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from walk(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk(v)

try:
    spec = yaml.load((base/'openapi-v0.1.yaml').read_text(encoding='utf-8'), Loader=UniqueLoader)
    validate_spec(spec)
    check('OpenAPI structural specification', True, spec['openapi'])
    ops = [(path, verb, op) for path, item in spec['paths'].items() for verb, op in item.items()
           if verb in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')]
    ids = [op['operationId'] for _, _, op in ops]
    check('Unique operation IDs', len(ids)==len(set(ids)), len(ids))
    check('Physical API prefix', all(p.startswith('/api/v1/') for p,_,_ in ops), len(spec['paths']))
    unresolved = []
    for obj in walk(spec):
        ref = obj.get('$ref')
        if ref and ref.startswith('#/'):
            value = spec
            try:
                for token in ref[2:].split('/'):
                    value = value[token.replace('~1','/').replace('~0','~')]
            except (KeyError, TypeError):
                unresolved.append(ref)
    check('OpenAPI local references resolve', not unresolved, unresolved)
    resolver = RefResolver.from_schema(spec)
    count, errors = 0, []
    for name, schema in spec['components']['schemas'].items():
        values = ([schema['example']] if 'example' in schema else []) + schema.get('examples', [])
        for example in values:
            count += 1
            for error in Draft202012Validator(schema, resolver=resolver).iter_errors(example):
                errors.append(f'{name}: {error.message}')
    check('Declared schema examples match contracts', not errors, {'count':count,'errors':errors})
except Exception as exc:
    spec, ops = {}, []
    check('OpenAPI parse/validation', False, str(exc))

try:
    sql = (base/'schema-v0.1.sql').read_text(encoding='utf-8-sig')
    tree = json.loads(parser.parse_sql_json(sql))
    creates = [obj['CreateStmt'] for obj in walk(tree) if 'CreateStmt' in obj]
    tables = {t['relation']['relname']: {e['ColumnDef']['colname'] for e in t.get('tableElts', []) if 'ColumnDef' in e} for t in creates}
    # ALTER ADD columns are part of the final schema as well.
    for obj in walk(tree):
        alt = obj.get('AlterTableStmt')
        if alt and alt['relation']['relname'] in tables:
            for cmd in alt.get('cmds', []):
                definition = cmd.get('AlterTableCmd', {}).get('def', {}).get('ColumnDef')
                if definition:
                    tables[alt['relation']['relname']].add(definition['colname'])
    check('DDL transaction closes', sql.rstrip().endswith('COMMIT;'), 'Design DDL is one transaction')
    functions = re.findall(r'CREATE FUNCTION .*?END \$\$;', sql, re.S)
    for function in functions:
        parser.parse_plpgsql_json(function)
    check('PL/pgSQL function syntax', bool(functions), {'functions': len(functions), 'note': 'syntax only; triggers not executed'})
    missing, fk_count = [], 0
    for obj in walk(tree):
        c = obj.get('Constraint')
        if not c or 'pktable' not in c:
            continue
        fk_count += 1
        target = c['pktable']['relname']
        if target not in tables:
            missing.append('table '+target)
        else:
            for col in c.get('pk_attrs', []):
                name = col.get('String', {}).get('sval')
                if name not in tables[target]:
                    missing.append(target+'.'+str(name))
    check('PostgreSQL DDL syntax', True, {'statements':len(tree['stmts']), 'tables':len(tables), 'note':'parser only; not executed in PostgreSQL'})
    check('Declared FK target tables/columns exist', not missing, {'foreign_keys':fk_count,'missing':missing})
    # PostgreSQL requires each referenced key to be backed by a PK/UNIQUE.
    unique_keys = {name:set() for name in tables}
    primary_keys = {}
    def collect_key(table, c, column=None):
        kind = c.get('contype')
        if kind not in ('CONSTR_PRIMARY','CONSTR_UNIQUE'):
            return
        key = tuple(x['String']['sval'] for x in c.get('keys', [])) or ((column,) if column else ())
        if key:
            unique_keys[table].add(frozenset(key))
            if kind == 'CONSTR_PRIMARY':
                primary_keys[table] = key
    for t in creates:
        name = t['relation']['relname']
        for e in t.get('tableElts', []):
            if 'Constraint' in e:
                collect_key(name, e['Constraint'])
            if 'ColumnDef' in e:
                for c in e['ColumnDef'].get('constraints', []):
                    collect_key(name, c.get('Constraint', {}), e['ColumnDef']['colname'])
    for obj in walk(tree):
        alt = obj.get('AlterTableStmt')
        if alt and alt['relation']['relname'] in tables:
            for cmd in alt.get('cmds', []):
                definition = cmd.get('AlterTableCmd', {}).get('def', {})
                if 'Constraint' in definition:
                    collect_key(alt['relation']['relname'], definition['Constraint'])
    invalid_keys = []
    for obj in walk(tree):
        c = obj.get('Constraint', {})
        if 'pktable' not in c:
            continue
        table = c['pktable']['relname']
        columns = tuple(x['String']['sval'] for x in c.get('pk_attrs', [])) or primary_keys.get(table, ())
        if not columns or frozenset(columns) not in unique_keys.get(table, set()):
            invalid_keys.append({'table':table,'columns':columns})
    check('Foreign key targets have declared unique keys', not invalid_keys, invalid_keys)

except Exception as exc:
    check('PostgreSQL DDL parse', False, str(exc))

try:
    seed = load('rbac-seed-v0.1.json')
    lab = json.loads((base/'../planning/lab-fixtures-v0.1.json').read_text(encoding='utf-8-sig'))
    flow = json.loads((base/'../use-cases/flow-fixtures-v0.2.json').read_text(encoding='utf-8-sig'))
    catalog = {p['code'] for p in seed['permission_catalog']}
    roles = {r['id']: r for r in seed['roles']}
    expected = {r['id']:set(r['permissions']) for r in lab['roles'] if r['application']=='VDT'}
    for ext in flow['permission_additions'] + seed['step05_permission_extensions']:
        expected[ext['role_id']].update(ext['permissions'])
    check('Seed exact baseline + FLOW + declared extensions', all(set(roles[k]['permissions'])==v for k,v in expected.items()) and set(roles)==set(expected), {k:sorted(v) for k,v in expected.items()})
    check('Seed original users/scopes/expiry unchanged', seed['users']==[u for u in lab['users'] if u['application']=='VDT'] and all(roles[r['id']]['scope']==r['scope'] for r in lab['roles'] if r['application']=='VDT') and seed['fixture_clock']==lab['fixture_clock'], 'VDT users only; no CRM provisioning')
    source_mismatch = [s['path'] for s in seed['source_fixtures'] if digest((base/s['path']).resolve())!=s['sha256']]
    check('Seed provenance hashes', not source_mismatch and flow['base_sha256']==digest((base/'../planning/lab-fixtures-v0.1.json').resolve()), source_mismatch)
    unknown, missing = [], []
    for path, verb, op in ops:
        permissions = op.get('x-required-permissions', [])
        for expr in permissions:
            for code in expr.split('|'):
                if code not in catalog:
                    unknown.append(f'{op["operationId"]}: {code}')
        if not permissions and op.get('security', spec.get('security', [])):
            # Authenticated session inspection/logout can be identity-only.
            if '/auth/' not in path:
                missing.append(f'{verb.upper()} {path}')
    check('API permissions exist in seed catalog', not unknown, unknown)
    check('Protected domain operations declare permissions', not missing, missing)
except Exception as exc:
    check('RBAC/contract consistency', False, str(exc))

try:
    cfg = load('config-template-v0.1.json')
    crm = cfg['crm_authentication_profile']
    required = ['challenge_ttl_seconds','max_attempt_limit','session_idle_timeout_seconds','rp_id','allowed_origins']
    check('CRM required fields unset until lab', crm['status']=='TO_SET_BEFORE_LAB' and all(k in crm['effective_values'] and crm['effective_values'][k] is None for k in required), required)
    check('CRM examples separated', [crm['illustrative_examples_not_effective'][k] for k in required[:3]]==[120,5,900], 'Examples are not runtime defaults')
    limits = cfg['vdt']['evidence']
    check('Upload limits consistent with design', [limits[k] for k in ['max_file_bytes','max_metadata_bytes','max_request_bytes']]==[20*1024**2,64*1024,21*1024**2], '20MiB /64KiB /21MiB')
    check('Runtime results remain NOT_RUN', set(cfg['runtime_test_status'].values())=={'NOT_RUN'}, cfg['runtime_test_status'])
except Exception as exc:
    check('Configuration semantics', False, str(exc))

try:
    manifest = load('input-manifest-v0.1.json')
    changed = [item['path'] for item in manifest['inputs'] if digest((base/item['path']).resolve())!=item['sha256']]
    check('Frozen inputs unchanged', not changed, {'inputs':len(manifest['inputs']),'changed':changed})
except Exception as exc:
    check('Frozen input manifest', False, str(exc))

broken = []
for md in base.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)', md.read_text(encoding='utf-8-sig')):
        if target.startswith(('http:','https:','mailto:','#')):
            continue
        link = unquote(target.split('#',1)[0].strip('<>'))
        if link and not (md.parent/link).exists():
            broken.append(md.name+': '+link)
check('Local Markdown file links', not broken, broken)

result = {'validation_scope':'STATIC_DESIGN_ONLY', 'runtime_tests':'NOT_RUN', 'checks':checks,
          'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks)}
rendered = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
if args.output:
    args.output.write_text(rendered, encoding='utf-8')
print(rendered)
raise SystemExit(1 if result['failed'] else 0)
