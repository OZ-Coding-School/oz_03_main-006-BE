from rest_framework import serializers

from .models import Comment, Image, Like, Post


# 전체 게시글 목록 나타내는 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


# 댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("post",)

    def get_nickname(self, obj):
        return obj.user_id.nickname  # User 모델의 nickname 필드를 가져옴


# 이미지 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", "board", "image", "created_at"]


# 게시글 상세 (댓글, 좋아요, 조회수, username 포함) 시리얼라이저
class DetailPostSerializer(serializers.ModelSerializer):
    # 커스텀 필드를 추가
    nickname = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.IntegerField(
        source="comments.count", read_only=True
    )  # 댓글 갯수
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = "__all__"

    # SerializerMethodField에서 호출될 메소드
    def get_nickname(self, obj):
        return obj.user_id.nickname  # User 모델의 nickname 필드를 가져옴

    def get_likes_count(self, obj):
        return Like.objects.filter(post=obj).count()


# 게시글 작성 시리얼라이저
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(
        many=True, read_only=True
    )  # 이미지 정보를 포함하기 위해 ImageSerializer 사용

    class Meta:
        model = Post
        fields = "__all__"
