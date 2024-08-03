from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response

from .models import Location, LocationImage
from .serializers import (
    HighlightSerializer,
    LocationImageSerializer,
    LocationSerializer,
)


# 모든 Location 객체의 목록을 제공하는 API 뷰
class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all().order_by(
        "location_id"
    )  # Location 객체들을 ID 순으로 정렬
    serializer_class = LocationSerializer  # 데이터를 직렬화할 때 사용할 Serializer 지정

    @swagger_auto_schema(
        operation_description="Get all locations",  # 이 API 엔드포인트의 설명
        responses={
            200: LocationSerializer(many=True)
        },  # 성공적인 응답 시 반환될 데이터 구조 정의
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request, *args, **kwargs
        )  # 부모 클래스의 get 메서드를 호출하여 응답 생성


# 특정 Location 객체의 세부 정보를 제공하는 API 뷰
class LocationDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()  # 모든 Location 객체를 대상으로 함
    serializer_class = LocationSerializer  # 데이터를 직렬화할 때 사용할 Serializer 지정

    @swagger_auto_schema(
        operation_description="Get a specific location",  # 이 API 엔드포인트의 설명
        responses={
            200: LocationSerializer()
        },  # 성공적인 응답 시 반환될 데이터 구조 정의
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request, *args, **kwargs
        )  # 부모 클래스의 get 메서드를 호출하여 응답 생성


# 모든 Location 객체의 하이라이트 목록을 제공하는 API 뷰
class HighlightListView(generics.ListAPIView):
    queryset = Location.objects.all().order_by(
        "location_id"
    )  # Location 객체들을 ID 순으로 정렬
    serializer_class = (
        HighlightSerializer  # 데이터를 직렬화할 때 사용할 Serializer 지정
    )

    @swagger_auto_schema(
        operation_description="Get highlights for all locations",  # 이 API 엔드포인트의 설명
        responses={
            200: HighlightSerializer(many=True)
        },  # 성공적인 응답 시 반환될 데이터 구조 정의
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request, *args, **kwargs
        )  # 부모 클래스의 get 메서드를 호출하여 응답 생성


# 특정 Location 객체의 하이라이트 세부 정보를 제공하는 API 뷰
class LocationHighlightDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()  # 모든 Location 객체를 대상으로 함
    serializer_class = (
        HighlightSerializer  # 데이터를 직렬화할 때 사용할 Serializer 지정
    )
    lookup_field = "location_id"  # URL에서 조회할 필드를 location_id로 설정

    @swagger_auto_schema(
        operation_description="Get highlights for a specific location",  # 이 API 엔드포인트의 설명
        responses={
            200: HighlightSerializer()
        },  # 성공적인 응답 시 반환될 데이터 구조 정의
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request, *args, **kwargs
        )  # 부모 클래스의 get 메서드를 호출하여 응답 생성


# 특정 Location 객체의 이미지 목록을 제공하는 API 뷰
class LocationImagesView(generics.ListAPIView):
    serializer_class = (
        LocationImageSerializer  # 데이터를 직렬화할 때 사용할 Serializer 지정
    )

    @swagger_auto_schema(
        operation_description="Get images for a specific location",  # 이 API 엔드포인트의 설명
        responses={
            200: LocationImageSerializer(many=True)
        },  # 성공적인 응답 시 반환될 데이터 구조 정의
    )
    def get(self, request, *args, **kwargs):
        # URL에서 location_id를 추출하여 해당 위치의 이미지를 필터링
        location_id = self.kwargs.get("location_id")
        images = LocationImage.objects.filter(location__location_id=location_id)
        serializer = self.get_serializer(images, many=True)  # 데이터를 직렬화
        return Response(serializer.data)  # 직렬화된 데이터를 응답으로 반환
