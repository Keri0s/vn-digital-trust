import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

class AppUserManager(BaseUserManager):
    def create_user(self, login_name, password=None, **fields):
        user=self.model(login_name=login_name,**fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class AppUser(AbstractBaseUser):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    organization_id=models.UUIDField()
    code=models.TextField(null=True,unique=True)
    login_name=models.TextField(unique=True)
    display_name=models.TextField()
    status=models.TextField(default='PENDING')
    version=models.BigIntegerField(default=1)
    password=models.TextField(db_column='password_hash')
    password_change_required=models.BooleanField(default=False)
    last_login=models.DateTimeField(db_column='last_login',null=True)
    email=models.TextField(null=True)
    USERNAME_FIELD='login_name'
    REQUIRED_FIELDS=['organization_id','display_name']
    objects=AppUserManager()
    @property
    def is_active(self): return self.status=='ACTIVE'
    class Meta:
        managed=False
        db_table='"vdt"."app_user"'
