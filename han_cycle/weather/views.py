from rest_framework import permissions, viewsets

from .models import Weather
from .serializers import WeatherSerializer


class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    날씨 정보 조회 API
    """

    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer
    filterset_fields = ["location_id", "fcst_date"]
