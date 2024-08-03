from locations.models import Location  # Location 모델 임포트
from rest_framework import serializers

from .models import Comment, Image, Like, Post


# 게시글 목록을 나타내는 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):
    # 좋아요 수와 닉네임을 커스텀 필드로 추가
    likes_count = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Post  # 연결할 모델
        fields = "__all__"  # 모든 필드를 포함

    # 해당 게시물에 대한 좋아요 수를 반환하는 메서드
    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    # 작성자의 닉네임을 반환하는 메서드
    def get_nickname(self, obj):
        return obj.user_id.nickname  # User 모델의 nickname 필드를 반환


# 댓글(Comment) 모델을 위한 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    # 닉네임과 프로필 이미지를 커스텀 필드로 추가
    nickname = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Comment  # 연결할 모델
        fields = "__all__"  # 모든 필드를 포함
        read_only_fields = ("post",)  # post 필드는 읽기 전용

    # 작성자의 닉네임을 반환하는 메서드
    def get_nickname(self, obj):
        return obj.user_id.nickname  # User 모델의 nickname 필드를 반환

    # 작성자의 프로필 이미지 URL을 반환하는 메서드
    def get_profile_image(self, obj):
        return (
            obj.user_id.profile_image.url if obj.user_id.profile_image else None
        )  # User 모델의 프로필 이미지 URL을 반환


# 이미지(Image) 모델을 위한 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image  # 연결할 모델
        fields = ["id", "board", "image", "created_at"]  # 포함할 필드 지정


# 게시글 상세 정보를 나타내는 시리얼라이저 (댓글, 좋아요, 조회수, 닉네임 등 포함)
class DetailPostSerializer(serializers.ModelSerializer):
    # 커스텀 필드를 추가하여 닉네임, 댓글, 댓글 수, 좋아요 수, 프로필 이미지를 포함
    nickname = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)  # 댓글 목록 포함
    comment_count = serializers.IntegerField(
        source="comments.count", read_only=True
    )  # 댓글 수를 반환
    likes_count = serializers.SerializerMethodField()
    location = serializers.SlugRelatedField(
        slug_field="city", read_only=True
    )  # 지역 필드를 도시 이름으로 반환
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Post  # 연결할 모델
        fields = "__all__"  # 모든 필드를 포함

    # 작성자의 닉네임을 반환하는 메서드
    def get_nickname(self, obj):
        return obj.user_id.nickname  # User 모델의 nickname 필드를 반환

    # 해당 게시물에 대한 좋아요 수를 반환하는 메서드
    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()

    # 작성자의 프로필 이미지 URL을 반환하는 메서드
    def get_profile_image(self, obj):
        return (
            obj.user_id.profile_image.url if obj.user_id.profile_image else None
        )  # User 모델의 프로필 이미지 URL을 반환


# 게시글 작성(Post) 모델을 위한 시리얼라이저
class PostSerializer(serializers.ModelSerializer):
    # 게시물에 포함된 이미지를 포함하기 위해 ImageSerializer를 사용
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post  # 연결할 모델
        fields = "__all__"  # 모든 필드를 포함
        ref_name = "BoardsPostSerializer"  # 충돌 방지를 위한 ref_name 추가
