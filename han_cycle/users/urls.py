from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    UserView,
    NicknameView,
    DeleteAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    path("accounts/register", RegisterView.as_view(), name="register"),
    path("accounts/login", LoginView.as_view(), name="login"),
    path("accounts/user", UserView.as_view(), name="user"),  # get token by cookie
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    path("accounts/nickname", NicknameView.as_view(), name="nickname"),
    path('accounts/delete', DeleteAccountView.as_view(), name='delete-account'),
    path('accounts/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('accounts/password-reset/confirm', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
