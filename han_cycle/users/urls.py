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
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import UserAPI, ProfileView, UserRetrieveUpdateAPIView

urlpatterns = [
    path('accounts/', include('allauth.urls')),  # Social login
    path("api/token/", TokenObtainPairView.as_view(), name="login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Added trailing slash for consistency
    path("api/user/", UserAPI.as_view(), name="user"),  # Added trailing slash for consistency
    path("accounts/profile/", ProfileView, name="profile"),  # Corrected usage of ProfileView
    path('accounts/update/',UserRetrieveUpdateAPIView.as_view(), name="update"),
]
