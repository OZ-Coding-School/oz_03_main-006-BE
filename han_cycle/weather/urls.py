from django.urls import path

from .views import (
    LatestWeatherView,
    TodayWeatherView,
    TomorrowWeatherView,
    WeatherForecastView,
)

# 이 weather 앱의 URL 패턴을 정의합니다.
urlpatterns = [
    # 특정 위치(location_id)에 대한 최신 날씨 정보를 가져오는 URL 패턴
    path(
        "latest/<int:location_id>/",
        LatestWeatherView.as_view(),
        name="latest_weather",
    ),
    # 특정 위치(location_id)에 대한 일기 예보(전체 기간)를 가져오는 URL 패턴
    path(
        "forecast/<int:location_id>/",
        WeatherForecastView.as_view(),
        name="weather_forecast",
    ),
    # 특정 위치(location_id)에 대한 오늘의 날씨 정보를 가져오는 URL 패턴
    path("today/<int:location_id>/", TodayWeatherView.as_view(), name="today_weather"),
    # 특정 위치(location_id)에 대한 내일의 날씨 정보를 가져오는 URL 패턴
    path(
        "tomorrow/<int:location_id>/",
        TomorrowWeatherView.as_view(),
        name="tomorrow_weather",
    ),
]
