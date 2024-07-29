from boards.models import Post
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


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "view_count", "thumbnail"]
        ref_name = "LocationPostSerializer"  # 충돌 방지를 위한 ref_name 추가


class LocationSerializer(serializers.ModelSerializer):
    images = LocationImageSerializer(many=True, read_only=True)
    top_posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            "location_id",
            "city",
            "popular_cities",
            "description",
            "highlights",
            "images",
            "l_category",
            "top_posts",  # top_posts 필드 추가
        ]
