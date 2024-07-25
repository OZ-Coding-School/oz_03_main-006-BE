from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from .models import Location, LocationImage
from .serializers import LocationSerializer, LocationDetailSerializer, HighlightSerializer

# 모든 위치 정보를 가져오는 API
class LocationListView(generics.ListAPIView):
    """
    모든 위치 정보를 가져오는 API
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @swagger_auto_schema(
        operation_description="Get a list of all locations",  # API 설명
        responses={200: LocationSerializer(many=True)}  # 응답 시리얼라이저 지정
    )
    def get(self, request, *args, **kwargs):
        """
        GET 메서드 처리 - 모든 위치 정보 조회
        """
        return super().get(request, *args, **kwargs)  # 부모 클래스의 get 메서드를 호출하여 처리

# 특정 위치 정보를 가져오는 API
class LocationDetailView(generics.RetrieveAPIView):
    """
    특정 위치 정보를 가져오는 API
    """
    queryset = Location.objects.all()
    serializer_class = LocationDetailSerializer
    lookup_field = 'location_id'  # URL에서 추출할 필드 지정

    @swagger_auto_schema(
        operation_description="Get details of a specific location",  # API 설명
        responses={200: LocationDetailSerializer(), 404: "Not Found"},  # 응답 시리얼라이저 및 상태 코드 지정
        manual_parameters=[
            openapi.Parameter('location_id', openapi.IN_PATH, description="ID of the location", type=openapi.TYPE_INTEGER)  # URL 파라미터 설명
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        GET 메서드 처리 - 특정 위치 정보 조회
        """
        return super().get(request, *args, **kwargs)  # 부모 클래스의 get 메서드를 호출하여 처리

# 하이라이트 정보를 가져오는 API
class HighlightView(APIView):
    """
    특정 위치의 하이라이트 정보를 가져오는 API
    """
    @swagger_auto_schema(
        operation_description="Get highlights of a specific location",  # API 설명
        responses={200: HighlightSerializer}  # 응답 시리얼라이저 지정
    )
    def get(self, request, pk):
        """
        GET 메서드 처리 - 특정 위치의 하이라이트 정보 조회
        """
        location = get_object_or_404(Location, pk=pk)
        serializer = HighlightSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 스크래핑을 수행하는 API
@swagger_auto_schema(
    method='get',
    operation_description="Scrape location data",  # API 설명
    responses={200: "Scraping completed successfully"}  # 응답 설명
)
@api_view(['GET'])
def scrape_location_data(request):
    """
    GET 메서드 처리 - 위치 데이터 스크래핑 수행
    """
    scrape_location_data_function()
    return Response({"message": "Scraping completed successfully"}, status=status.HTTP_200_OK)