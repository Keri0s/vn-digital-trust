"""Install only a salted verifier for the two disposable browser QA accounts.

The browser tool retains the plaintext only in its memory. Never use on the lab.
"""
import os
import sys
sys.path.insert(0,'/app/lab/local')
import database
import psycopg

if os.environ.get('PGHOST')!='testdb' or os.environ.get('VDT_AUTH_INTEGRATION_TEST')!='true':
    raise SystemExit('Disposable browser testdb only.')
value=os.environ.get('VDT_BROWSER_PASSWORD_HASH','')
parts=value.split('$')
if len(parts)!=4 or parts[0]!='pbkdf2_sha256' or not parts[1].isdigit() or int(parts[1])<1000000:
    raise SystemExit('A salted test verifier is required; plaintext is not accepted.')
with psycopg.connect(**database.parameters()) as connection:
    names={r[0] for r in connection.execute('SELECT login_name FROM vdt.app_user').fetchall()}
    if names!={'assessment-admin','assessment-security','assessment-reviewer','assessment-risk-owner'}:
        raise SystemExit('Unexpected accounts: refusing browser fixture update.')
    connection.execute('''UPDATE vdt.app_user SET password_hash=%s,version=version+1
        WHERE login_name IN ('assessment-security','assessment-reviewer')''',(value,))
print('Disposable browser verifier installed; no plaintext written.')
