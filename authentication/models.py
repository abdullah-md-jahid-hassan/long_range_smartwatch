from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from authentication.managers.user import UserManager
from core.models import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email      = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    # Overrides BaseModel's SoftDeleteManager — Django auth requires the default
    # manager to return all users, including soft-deleted ones.
    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.id} - {self.email}"
