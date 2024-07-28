from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from locations.models import Location
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Weather
from .serializers import WeatherSerializer


class WeatherForecastView(APIView):
    @swagger_auto_schema(
        operation_description="Get weather forecast for a specific location",
        responses={200: WeatherSerializer(many=True), 404: "Location not found"},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="ID of the location",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, location_id):
        location = get_object_or_404(Location, location_id=location_id)
        weather_forecast = Weather.objects.filter(location=location).order_by(
            "fcst_date", "base_time"
        )

        if not weather_forecast.exists():
            return Response(
                {"error": "Weather data not found for this location"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WeatherSerializer(weather_forecast, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
