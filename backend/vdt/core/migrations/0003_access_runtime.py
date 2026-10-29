"""Require replacement of administrator-issued temporary credentials."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0002_auth_runtime')]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.RunSQL(
                'ALTER TABLE vdt.app_user ADD COLUMN password_change_required boolean NOT NULL DEFAULT false;',
                reverse_sql=None)],
            state_operations=[migrations.AddField(
                model_name='appuser', name='password_change_required',
                field=models.BooleanField(default=False))],
        ),
    ]
