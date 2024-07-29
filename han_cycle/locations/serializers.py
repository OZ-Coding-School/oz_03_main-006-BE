# locations/serializers.py
from rest_framework import serializers

from .models import Location, LocationImage


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["location_id", "highlights"]


class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage
        fields = ["image_url"]


class LocationSerializer(serializers.ModelSerializer):
    images = LocationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            "location_id",
            "city",
            "popular_cities",
            "description",
            "highlights",
            "images",
        ]
