from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Weather
from .serializers import WeatherSerializer
from locations.models import Location
from django.shortcuts import get_object_or_404

class WeatherForecastView(APIView):
    @swagger_auto_schema(
        operation_description="Get weather forecast for a specific location",
        responses={
            200: WeatherSerializer(many=True),
            404: "Location not found"
        },
        manual_parameters=[
            openapi.Parameter('location_id', openapi.IN_PATH, description="ID of the location", type=openapi.TYPE_INTEGER)
        ]
    )
    def get(self, request, location_id):
        """
        특정 위치의 날씨 예보를 조회합니다.
        """
        location = get_object_or_404(Location, id=location_id)
        weather_forecast = Weather.objects.filter(location=location)
        serializer = WeatherSerializer(weather_forecast, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)