from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Unique
    provider = models.CharField(max_length=100)  # Not null
    nickname = models.CharField(max_length=100)  # Unique, not null
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp with default value of now
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Corrected this to plural
    