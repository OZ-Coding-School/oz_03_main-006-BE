from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)  # Primary key, auto-incrementing integer
    email = models.EmailField(unique=True)  # Unique email field
    password = models.CharField(max_length=128)  # Password field
    provider = models.CharField(max_length=100)  # Provider field, not null
    social_id = models.CharField(max_length=100)  # Social ID field, not null
    nickname = models.CharField(max_length=100)  # Nickname field, not null
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp with default value of now

    def __str__(self):
        return self.nickname or self.email
