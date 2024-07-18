# api/serializers.py

from rest_framework import serializers
from .models import User, Post, PostImage, Location, Profile, Weather, Tag, PostLocation, Comment, Like, Category, LocationCategory, PostTag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'provider', 'social_id', 'nickname', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},  # 비밀번호는 쓰기 전용으로 설정
        }


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image_id', 'image_url', 'is_representative', 'created_at']


class LocationSerializer(serializers.ModelSerializer):
    weather = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['location_id', 'city', 'district', 'symbol', 'population', 'information', 'category', 'image_url', 'weather']

    def get_weather(self, obj):
        today = datetime.date.today()
        # 현재 시간을 KST timezone에 맞춰서 가져오기
        now = datetime.datetime.now(timezone.utc).astimezone(timezone('Asia/Seoul'))
        base_time = now.strftime('%H%M')  # 현재 시간 (HHMM 형식)

        # 날씨 정보 가져오기 (가장 최근 base_date, base_time을 기준으로 fcst_date가 오늘인 데이터)
        weather = Weather.objects.filter(
            location=obj,
            fcst_date=today
        ).order_by('-base_date', '-base_time').first()

        if weather:
            return WeatherSerializer(weather).data
        return None


class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['profile_id', 'nickname', 'user_id', 'introduction', 'profile_image']

    def get_profile_image(self, obj):
        active_profile_image = obj.user.profile_images.filter(is_active=True).first()
        if active_profile_image:
            return active_profile_image.image_url
        return None  # 활성화된 이미지가 없을 경우 None 반환
    
# class ProfileImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProfileImage
#         fields = ['image_id', 'user_id', 'image_url', 'is_active', 'created_at']


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = ['location_id', 'base_date', 'base_time', 'fcst_date', 'category', 'fcst_value']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'name']


class PostLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLocation
        fields = ['post_id', 'location_id']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()  # 댓글 정보는 메서드 필드로 처리
    likes_count = serializers.SerializerMethodField()  # 좋아요 수는 메서드 필드로 처리
    representative_image_url = serializers.SerializerMethodField()  # representative_image_url 필드 추가

    class Meta:
        model = Post
        fields = ['post_id', 'user', 'title', 'body', 'created_at', 'updated_at', 'view_count', 
                  'travel_start_date', 'travel_end_date', 'images', 'locations', 'tags', 'comments', 'likes_count']

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_representative_image_url(self, obj):
        representative_image = obj.images.filter(is_representative=True).first()
        if representative_image:
            return representative_image.image_url
        return None


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['comment_id', 'post_id', 'user', 'content', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['like_id', 'post_id', 'user_id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name']


class LocationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationCategory
        fields = ['location_id', 'category_id']

class PostTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTag
        fields = ['post_id', 'tag_id']