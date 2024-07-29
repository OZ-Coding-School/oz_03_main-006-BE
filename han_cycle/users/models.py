from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager  # Import the custom manager

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Unique
    provider = models.CharField(max_length=100)  # Not null
    nickname = models.CharField(max_length=100, unique=True)  # Unique, not null
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp with default value of now
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email']  # Added email to required fields

    objects = CustomUserManager()  # Set the custom manager
