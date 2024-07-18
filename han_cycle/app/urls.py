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
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
#from rest_framework import permissions    #API인증허가/제어

schema_view = get_schema_view(
    openapi.Info(
        title="HanCycle API",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    #permission_classes=(permissions.AllowAny,),   #인증허가 모두에게
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin 추가
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

