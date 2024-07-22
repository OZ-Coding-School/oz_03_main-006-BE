from rest_framework import serializers
from .models import Post, Comment, Image

#전체 게시글 목록 나타내는 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

#댓글 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('post',)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'board', 'image','created_at']

#게시글 상세 (댓글, 좋아요, 조회수 포함) 시리얼라이저
class DetailPostSerializer(serializers.ModelSerializer):
    # comment_set = serializers.PrimaryKeyRelatedField(many= True, read_only=True) # 이러면 게시글 당 댓글키만 나오게됨
    comments = CommentSerializer(many=True, read_only=True) # CommentSerializer정의가 이 코드보다 밑에 있다면 에러가 발생할 수 있음. json 안에 json 이 있는 형태가 됨
    comment_count = serializers.IntegerField(source='comments.count', read_only=True) # 댓글 갯수
    class Meta:
        model = Post
        fields = '__all__'
        
#게시글 작성 시리얼라이저
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)  # 이미지 정보를 포함하기 위해 ImageSerializer 사용

    class Meta:
        model = Post
        fields = '__all__'