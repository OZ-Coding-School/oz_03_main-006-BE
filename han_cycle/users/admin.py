from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import User

class ProfileInline(admin.StackedInline):
    model = User
    can_delete = False  # This is the correct attribute to prevent deletion

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
