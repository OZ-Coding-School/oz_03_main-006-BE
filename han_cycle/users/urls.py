from django.urls import path

from .views import (
    GoogleCallbackView,
    KakaoLoginView,
    LoginView,
    LogoutView,
    RegisterView,
    UserView,
    edit_profile,
    googleredirect,
    kakaoredirect,
)

urlpatterns = [
    path("accounts/register", RegisterView.as_view(), name="register"),
    path("accounts/login", LoginView.as_view(), name="login"),
    path("accounts/user", UserView.as_view(), name="user"),
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path("accounts/google/login", googleredirect, name="google_login"),
    path(
        "accounts/google/login/callback/",
        GoogleCallbackView.as_view(),
        name="google_callback",
    ),
    path("accounts/kakao/login", kakaoredirect, name="kakao_login"),
    path(
        "accounts/kakao/login/callback/",
        KakaoLoginView.as_view(),
        name="kakao_callback",
    ),
    path("accounts/profile/edit", edit_profile, name="edit_profile"),
]
