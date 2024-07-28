# urls.py
from django.urls import path

from .views import LatestWeatherView, WeatherForecastView

urlpatterns = [
    path(
        "weather/latest/<int:location_id>/",
        LatestWeatherView.as_view(),
        name="latest_weather",
    ),
    path(
        "weather/forecast/<int:location_id>/",
        WeatherForecastView.as_view(),
        name="weather_forecast",
    ),
]
