from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Post, PostImage, Location, Profile, Weather, Tag, PostLocation, Comment, Like, Category, LocationCategory, PostTag
from .serializers import (
    UserSerializer, PostSerializer, PostImageSerializer, LocationSerializer, ProfileSerializer,
    WeatherSerializer, TagSerializer, PostLocationSerializer, CommentSerializer, LikeSerializer, 
    CategorySerializer, LocationCategorySerializer, PostTagSerializer
)

# --- 회원 관련 ---
class UserViewSet(viewsets.ModelViewSet):
    """
    사용자 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    """
    프로필 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


# class ProfileImageViewSet(viewsets.ModelViewSet):
#     """
#     프로필 이미지 관련 CRUD API를 제공하는 뷰셋입니다.
#     """
#     queryset = ProfileImage.objects.all()
#     serializer_class = ProfileImageSerializer


# --- 게시글 관련 ---
class PostViewSet(viewsets.ModelViewSet):
    """
    게시글 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        """게시글 조회 시 조회수 증가"""
        post = get_object_or_404(Post, pk=pk)
        post.view_count += 1
        post.save()
        serializer = self.get_serializer(post)
        return Response(serializer.data)


class PostImageViewSet(viewsets.ModelViewSet):
    """
    게시글 이미지 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer


class PostLocationViewSet(viewsets.ModelViewSet):
    """
    게시글 위치 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = PostLocation.objects.all()
    serializer_class = PostLocationSerializer

class PostTagViewSet(viewsets.ModelViewSet):
    """
    게시글 태그 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = PostTag.objects.all()
    serializer_class = PostTagSerializer

# --- 지역 관련 ---
class LocationViewSet(viewsets.ModelViewSet):
    """
    지역 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class WeatherViewSet(viewsets.ModelViewSet):
    """
    날씨 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer


# --- 기타 ---
class TagViewSet(viewsets.ModelViewSet):
    """
    태그 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    카테고리 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LocationCategoryViewSet(viewsets.ModelViewSet):
    """
    지역 카테고리 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = LocationCategory.objects.all()
    serializer_class = LocationCategorySerializer

# --- 댓글/좋아요 관련 ---
class CommentViewSet(viewsets.ModelViewSet):
    """
    댓글 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    """
    좋아요 관련 CRUD API를 제공하는 뷰셋입니다.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
