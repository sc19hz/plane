# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from random import randint
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, password, **extra_fields)

    def _create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    real_name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['real_name']
    def save(self, *args, **kwargs):
        while not self.pk:
            user_id = randint(10000000, 99999999)  # Generate a random 8-digit number
            if not CustomUser.objects.filter(user_id=user_id).exists():
                self.user_id = user_id
                break
        super(CustomUser, self).save(*args, **kwargs)
    def __str__(self):
        return self.username
