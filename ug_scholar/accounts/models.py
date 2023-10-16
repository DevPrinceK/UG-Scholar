from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from accounts.manager import AccountManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=100, unique=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    objects = AccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.fullname or self.email 

    class Meta:
        db_table = 'user'


class UserLog(models.Model):
    '''Logs crucial user actions'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.action

    class Meta:
        db_table = 'user_log'