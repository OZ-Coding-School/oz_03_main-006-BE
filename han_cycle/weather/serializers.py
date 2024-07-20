from rest_framework import serializers

from .models import Weather


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = [
            "location_id",
            "base_date",
            "base_time",
            "fcst_date",
            "W_category",
            "fcst_value",
        ]
