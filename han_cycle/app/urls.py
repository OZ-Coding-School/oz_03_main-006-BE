"""
URL configuration for han_cycle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin  # Django 관리자 페이지를 위한 모듈
from django.urls import include, path  # URL 경로를 설정하기 위한 모듈
from drf_yasg import openapi  # Swagger/OpenAPI 문서 생성을 위한 모듈
from drf_yasg.views import get_schema_view  # Swagger/OpenAPI UI 생성을 위한 뷰
from rest_framework import permissions  # API 권한 관리를 위한 모듈

from .views import health_check  # 서버 상태 확인을 위한 헬스 체크 뷰

# Swagger 설정: API 문서를 위한 스키마 뷰 생성
schema_view = get_schema_view(
    openapi.Info(
        title="HanCycle API",  # API 제목
        default_version="v1",  # API 버전
        description="API description",  # API 설명
        terms_of_service="https://www.google.com/policies/terms/",  # 서비스 약관 URL
    ),
    public=True,  # 공개 접근 가능 여부 설정
    permission_classes=(permissions.AllowAny,),  # 모든 사용자에게 접근 허용
)

# URL 패턴 정의: 각 앱의 URL과 뷰를 연결
urlpatterns = [
    path("admin/", admin.site.urls),  # 관리자 페이지 경로
    path("users/", include("users.urls")),  # 사용자 관련 URL 패턴 포함
    path("posts/", include("boards.urls")),  # 게시물 관련 URL 패턴 포함
    path("weather/", include("weather.urls")),  # 날씨 관련 URL 패턴 포함
    path("search/", include("search.urls")),  # 검색 기능 관련 URL 패턴 포함
    path("locations/", include("locations.urls")),  # 위치 관련 URL 패턴 포함
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),  # Swagger UI 경로 설정
    path(
        "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),  # ReDoc UI 경로 설정
    path("home/health/", health_check, name="health_check"),  # 헬스 체크 엔드포인트
]
