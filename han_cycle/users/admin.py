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

# # django.contrib.auth.models에서 User 모델을 import 하지 않고, 커스텀 User 모델이 있는 users.models에서 import
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

# from .models import Profile, User


# # user 모델 안에서 prifile 관리
# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False


# # User 모델을 admin 페이지에 등록하지만, 직접 커스터마이징한 User 모델을 사용하도록 설정// admin.site.register(User, CustomUserAdmin)는 커스텀유저 사용으로 불필요
# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)
#     # 추가적으로 필요한 관리자 필드 설정들
#     # 예: list_display = ('username', 'email', 'provider', 'social_id', 'created_at')


# admin.site.register(User, CustomUserAdmin)
