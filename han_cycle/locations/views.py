from boards.models import Post
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response

from .models import Location, LocationImage
from .serializers import (
    HighlightSerializer,
    LocationImageSerializer,
    LocationSerializer,
    PostSerializer,
)


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
        location = self.get_object()
        top_posts = Post.objects.filter(location=location).order_by("-view_count")[:8]
        top_posts_data = PostSerializer(top_posts, many=True).data

        location_data = self.get_serializer(location).data
        location_data["top_posts"] = top_posts_data

        return Response(location_data)


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


class LocationImagesView(generics.ListAPIView):
    serializer_class = LocationImageSerializer

    @swagger_auto_schema(
        operation_description="Get images for a specific location",
        responses={200: LocationImageSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        location_id = self.kwargs.get("location_id")
        images = LocationImage.objects.filter(location__location_id=location_id)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)
