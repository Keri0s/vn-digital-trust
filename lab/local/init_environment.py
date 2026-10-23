"""Create local development secrets once; never print or overwrite secrets."""
import os
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[2]
runtime = ROOT / '.runtime'
runtime.mkdir(mode=0o700, exist_ok=True)
(runtime / 'checks').mkdir(mode=0o700, exist_ok=True)
target = runtime / 'local.env'
if target.exists():
    print('Existing local environment preserved.')
else:
    values = {name: secrets.token_urlsafe(48) for name in (
        'VDT_DB_OWNER_PASSWORD', 'VDT_DB_APP_PASSWORD', 'VDT_SECRET_KEY')}
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as output:
        output.write(''.join(f'{key}={value}\n' for key, value in values.items()))
    print('Created ignored local environment. No CRM profile was configured.')
