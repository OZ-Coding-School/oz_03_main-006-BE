# urls.py
from django.urls import path

from .views import (
    LatestWeatherView,
    TodayWeatherView,
    TomorrowWeatherView,
    WeatherForecastView,
)

urlpatterns = [
    path(
        "latest/<int:location_id>/",
        LatestWeatherView.as_view(),
        name="latest_weather",
    ),
    path(
        "forecast/<int:location_id>/",
        WeatherForecastView.as_view(),
        name="weather_forecast",
    ),
    path("today/<int:location_id>/", TodayWeatherView.as_view(), name="today_weather"),
    path(
        "tomorrow/<int:location_id>/",
        TomorrowWeatherView.as_view(),
        name="tomorrow_weather",
    ),
]
