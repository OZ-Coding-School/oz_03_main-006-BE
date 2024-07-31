from django.urls import path

from .views import (
    EditProfileView,
    LoginView,
    LogoutView,
    RegisterView,
    UserView,
)

urlpatterns = [
    path("accounts/register", RegisterView.as_view(), name="register"),
    path("accounts/login", LoginView.as_view(), name="login"),
    path("accounts/user", UserView.as_view(), name="user"),  # get token by cookie
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path(
        "accounts/profile/edit", EditProfileView.as_view(), name="edit_profile"
    ),  # 프로필 수정 엔드포인트
]
