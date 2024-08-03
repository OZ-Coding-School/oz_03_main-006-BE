from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from locations.models import Location
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Weather
from .serializers import WeatherSerializer


# 특정 위치의 최신 날씨 데이터를 조회하는 API 뷰
class LatestWeatherView(APIView):
    @swagger_auto_schema(
        operation_description="특정 위치의 최신 날씨 예보 가져오기",
        responses={200: WeatherSerializer, 404: "위치를 찾을 수 없음"},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="ID of the location",  # 위치 ID 설명
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, location_id):
        # 주어진 location_id에 해당하는 Location 객체를 가져옵니다. 없을 경우 404 오류를 반환합니다.
        location = get_object_or_404(Location, location_id=location_id)
        # 해당 위치의 최신 날씨 데이터를 가져옵니다. 예보 날짜와 기준 시간을 기준으로 내림차순 정렬하여 가장 최근 데이터를 선택합니다.
        latest_weather = (
            Weather.objects.filter(location=location)
            .order_by("-fcst_date", "-base_time")
            .first()
        )

        # 만약 날씨 데이터가 없는 경우, 404 오류를 반환합니다.
        if not latest_weather:
            return Response(
                {"error": "이 위치에 대한 날씨 데이터를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 데이터를 직렬화하여 응답으로 반환합니다.
        serializer = WeatherSerializer(latest_weather)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 특정 위치의 전체 날씨 예보 데이터를 가져오는 API 뷰
class WeatherForecastView(APIView):
    @swagger_auto_schema(
        operation_description="특정 위치의 날씨 예보 가져오기",
        responses={200: WeatherSerializer(many=True), 404: "위치를 찾을 수 없음"},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="위치 ID",  # 위치 ID 설명
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, location_id):
        # 주어진 location_id에 해당하는 Location 객체를 가져옵니다. 없을 경우 404 오류를 반환합니다.
        location = get_object_or_404(Location, location_id=location_id)
        # 해당 위치의 모든 날씨 예보 데이터를 가져옵니다. 예보 날짜와 기준 시간을 기준으로 오름차순 정렬합니다.
        weather_forecast = Weather.objects.filter(location=location).order_by(
            "fcst_date", "base_time"
        )

        # 만약 날씨 예보 데이터가 없는 경우, 404 오류를 반환합니다.
        if not weather_forecast.exists():
            return Response(
                {"error": "이 위치에 대한 날씨 데이터를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 데이터를 직렬화하여 응답으로 반환합니다.
        serializer = WeatherSerializer(weather_forecast, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 특정 위치의 오늘 날씨 데이터를 가져오는 API 뷰
class TodayWeatherView(APIView):
    @swagger_auto_schema(
        operation_description="특정 위치의 오늘 날씨 데이터 가져오기",
        responses={200: WeatherSerializer(many=True), 404: "위치를 찾을 수 없음"},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="위치 ID",  # 위치 ID 설명
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, location_id):
        # 오늘의 날짜를 "YYYYMMDD" 형식으로 가져옵니다.
        today_date = datetime.now().strftime("%Y%m%d")
        # 주어진 location_id에 해당하는 Location 객체를 가져옵니다. 없을 경우 404 오류를 반환합니다.
        location = get_object_or_404(Location, location_id=location_id)
        # 해당 위치의 오늘 날짜에 대한 날씨 데이터를 가져옵니다. 예보 날짜와 기준 시간을 기준으로 오름차순 정렬합니다.
        today_weather = Weather.objects.filter(
            location=location, fcst_date=today_date
        ).order_by("fcst_date", "base_date")

        # 만약 오늘의 날씨 데이터가 없는 경우, 404 오류를 반환합니다.
        if not today_weather.exists():
            return Response(
                {"error": "이 위치에 대한 오늘의 날씨 데이터를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 데이터를 직렬화하여 응답으로 반환합니다.
        serializer = WeatherSerializer(today_weather, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 특정 위치의 내일 날씨 데이터를 가져오는 API 뷰
class TomorrowWeatherView(APIView):
    @swagger_auto_schema(
        operation_description="특정 위치의 내일 날씨 데이터 가져오기",
        responses={200: WeatherSerializer(many=True), 404: "위치를 찾을 수 없음"},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="위치 ID",  # 위치 ID 설명
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, location_id):
        # 내일의 날짜를 "YYYYMMDD" 형식으로 가져옵니다.
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        # 주어진 location_id에 해당하는 Location 객체를 가져옵니다. 없을 경우 404 오류를 반환합니다.
        location = get_object_or_404(Location, location_id=location_id)
        # 해당 위치의 내일 날짜에 대한 날씨 데이터를 가져옵니다. 예보 날짜와 기준 시간을 기준으로 오름차순 정렬합니다.
        tomorrow_weather = Weather.objects.filter(
            location=location, fcst_date=tomorrow_date
        ).order_by("fcst_date", "base_date")

        # 만약 내일의 날씨 데이터가 없는 경우, 404 오류를 반환합니다.
        if not tomorrow_weather.exists():
            return Response(
                {"error": "이 위치에 대한 내일의 날씨 데이터를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 데이터를 직렬화하여 응답으로 반환합니다.
        serializer = WeatherSerializer(tomorrow_weather, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
