"""Operational login limiter, separate from immutable domain history."""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.RunSQL('''
        CREATE TABLE vdt.auth_rate_bucket (
            bucket_key text PRIMARY KEY CHECK (bucket_key ~ '^[0-9a-f]{64}$'),
            window_started_at timestamptz NOT NULL,
            failures integer NOT NULL DEFAULT 0 CHECK (failures >= 0),
            locked_until timestamptz
        );
        CREATE INDEX vdt_session_active_user_idx ON vdt.vdt_session(user_id)
            WHERE revoked_at IS NULL;
    ''', reverse_sql=None)]
