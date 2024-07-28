from rest_framework import serializers

from .models import Weather


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = [
            "location",
            "base_date",
            "fcst_date",
            "base_time",
            "POP",
            "TMX",
            "TMN",
            "SKY",
            "fcst_value",
        ]
