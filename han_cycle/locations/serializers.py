from rest_framework import serializers
from .models import Location, LocationImage

# Location 모델의 리스트 조회를 위한 시리얼라이저
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location  # 사용할 모델 지정
        fields = ['location_id', 'city', 'popular_cities', 'description', 'highlights']  # 포함할 필드 지정

# LocationImage 모델의 이미지를 위한 시리얼라이저
class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage  # 사용할 모델 지정
        fields = ['image_url']  # 포함할 필드 지정

# Location 모델의 상세 조회를 위한 시리얼라이저
class LocationDetailSerializer(serializers.ModelSerializer):
    images = LocationImageSerializer(many=True, read_only=True)  # 중첩 시리얼라이저를 이용해 이미지를 포함

    class Meta:
        model = Location  # 사용할 모델 지정
        fields = ['location_id', 'city', 'popular_cities', 'description', 'highlights', 'images']  # 포함할 필드 지정

class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['highlights']