from uuid import uuid4

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .enums import LawyerTypeEnum


class Usermanager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    external_id = models.UUIDField(default=uuid4, unique=True, db_index=True)
    username = None
    name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_lawyer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = Usermanager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class LawyerMetadata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lawyer_meta")
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    lawyer_type = models.IntegerField(choices=LawyerTypeEnum.choices, default=LawyerTypeEnum.GENERAL)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    call_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
