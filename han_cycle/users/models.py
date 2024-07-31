from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from search.search_index import UserIndex
import uuid
from .managers import CustomUserManager  # Import the custom manager
from django.conf import settings
import datetime

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Unique
    provider = models.CharField(max_length=100)  # Not null
    nickname = models.CharField(max_length=100, unique=True)  # Unique, not null
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(
        default=timezone.now
    )  # Timestamp with default value of now
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )

    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS = ["email"]  # Added email to required fields

    objects = CustomUserManager()  # Set the custom manager

    def indexing(self):
        obj = UserIndex(meta={"id": self.id}, nickname=self.nickname, email=self.email)
        obj.save()
        return obj.to_dict(include_meta=True)
    

class RefreshToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at
