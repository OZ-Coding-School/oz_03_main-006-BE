from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from .models import Location
from .serializers import HighlightSerializer, LocationSerializer


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all().order_by("location_id")
    serializer_class = LocationSerializer

    @swagger_auto_schema(
        operation_description="Get all locations",
        responses={200: LocationSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LocationDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @swagger_auto_schema(
        operation_description="Get a specific location",
        responses={200: LocationSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class HighlightListView(generics.ListAPIView):
    queryset = Location.objects.all().order_by("location_id")
    serializer_class = HighlightSerializer

    @swagger_auto_schema(
        operation_description="Get highlights for all locations",
        responses={200: HighlightSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LocationHighlightDetailView(generics.RetrieveAPIView):
    queryset = Location.objects.all()
    serializer_class = HighlightSerializer
    lookup_field = "location_id"

    @swagger_auto_schema(
        operation_description="Get highlights for a specific location",
        responses={200: HighlightSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
