from rest_framework import serializers

from .models import Weather


class WeatherSerializer(serializers.ModelSerializer):
    sky_status = serializers.SerializerMethodField()

    class Meta:
        model = Weather
        fields = [
            "location",
            "base_date",
            "fcst_date",
            "base_time",
            "POP",
            "TMP",
            "SKY",
            "sky_status",
        ]

    def get_sky_status(self, obj):
        return obj.get_sky_status()
