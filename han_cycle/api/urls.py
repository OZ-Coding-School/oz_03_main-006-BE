from django.urls import path, include
from rest_framework.routers import DefaultRouter   

from .views import (
    UserViewSet, 
    PostViewSet, 
    PostImageViewSet, 
    LocationViewSet, 
    ProfileViewSet,
    WeatherViewSet,
    TagViewSet,
    PostLocationViewSet,
    CommentViewSet,
    LikeViewSet,
    CategoryViewSet,
    LocationCategoryViewSet,
    #ProfileImageViewSet,
    PostTagViewSet  
)

router = DefaultRouter()

# 회원 관련
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

# 게시글 관련
router.register(r'posts', PostViewSet)
router.register(r'post-images', PostImageViewSet)
router.register(r'post-locations', PostLocationViewSet)
router.register(r'post-tags', PostTagViewSet)  # PostTagViewSet 등록 (수정)

# 지역 관련
router.register(r'locations', LocationViewSet)
router.register(r'weather', WeatherViewSet)

# 기타
router.register(r'tags', TagViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'location-categories', LocationCategoryViewSet)

# 댓글
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
