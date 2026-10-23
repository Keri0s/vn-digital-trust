from pathlib import Path
from django.db import migrations,models
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[migrations.RunSQL(Path(__file__).with_suffix('.sql').with_name('0001_domain.sql').read_text(encoding='utf-8'),reverse_sql=None),migrations.CreateModel(name='AppUser',fields=[('id',models.UUIDField(primary_key=True,serialize=False)),('organization_id',models.UUIDField()),('code',models.TextField(null=True,unique=True)),('login_name',models.TextField(unique=True)),('display_name',models.TextField()),('status',models.TextField(default='PENDING')),('version',models.BigIntegerField(default=1)),('password',models.TextField(db_column='password_hash')),('last_login',models.DateTimeField(db_column='last_login',null=True)),('email',models.TextField(null=True))],options={'managed':False,'db_table':'"vdt"."app_user"'})]
