from rest_framework import serializers

from .models import Location, LocationImage


# Location 모델의 하이라이트 필드를 직렬화하는 클래스
class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location  # 직렬화할 모델을 지정
        fields = [
            "location_id",
            "highlights",
        ]  # 직렬화할 필드를 지정 (location_id, highlights)


# LocationImage 모델을 직렬화하는 클래스
class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage  # 직렬화할 모델을 지정
        fields = ["image_url"]  # 직렬화할 필드를 지정 (image_url)


# Location 모델을 직렬화하는 클래스
class LocationSerializer(serializers.ModelSerializer):
    # images 필드는 LocationImageSerializer를 사용하여 직렬화됩니다. 다대다 관계이므로 many=True를 사용.
    images = LocationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Location  # 직렬화할 모델을 지정
        fields = [
            "location_id",  # 위치 ID
            "city",  # 도시 이름
            "popular_cities",  # 인기 있는 도시 목록
            "description",  # 도시 설명
            "highlights",  # 주요 하이라이트
            "images",  # 연관된 이미지 목록
            "l_category",  # 위치 카테고리
        ]  # 직렬화할 필드를 지정
