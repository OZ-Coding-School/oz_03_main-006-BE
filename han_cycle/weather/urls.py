from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WeatherViewSet

router = DefaultRouter()
router.register(r"weather", WeatherViewSet, basename="weather")

urlpatterns = [
    path("", include(router.urls)),
]
