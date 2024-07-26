from django.urls import path
from . import views

urlpatterns = [
    path('forecast/<int:location_id>/', views.WeatherForecastView.as_view(), name='weather_forecast'),
]
