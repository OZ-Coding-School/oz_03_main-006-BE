from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    GoogleCallbackView,
    KakaoLoginView,
    LoginView,
    LogoutView,
    RegisterView,
    UserView,
    googleredirect,
    kakaoredirect,
    edit_profile,
)

urlpatterns = [
    # 사용자 등록 (회원가입) API 엔드포인트
    path("accounts/register", RegisterView.as_view(), name="register"),
    # 로그인 API 엔드포인트
    path("accounts/login", LoginView.as_view(), name="login"),
    # 사용자 정보 조회 API 엔드포인트 (JWT 토큰 필요)
    path("accounts/user", UserView.as_view(), name="user"),
    # 로그아웃 API 엔드포인트
    path("accounts/logout", LogoutView.as_view(), name="logout"),
    # 구글 소셜 로그인 리다이렉트 엔드포인트
    path("accounts/google/login", googleredirect, name="google_login"),
    # 구글 소셜 로그인 콜백 엔드포인트
    path(
        "accounts/google/login/callback/",
        GoogleCallbackView.as_view(),
        name="google_callback",
    ),
    # 카카오 소셜 로그인 리다이렉트 엔드포인트
    path("accounts/kakao/login", kakaoredirect, name="kakao_login"),
    # 카카오 소셜 로그인 콜백 엔드포인트
    path(
        "accounts/kakao/login/callback/",
        KakaoLoginView.as_view(),
        name="kakao_callback",
    ),
    #프로필 수정 API 엔드포인트
     path('edit-profile/', edit_profile, name='edit_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
