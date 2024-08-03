from django.db import models
from django.utils import timezone
from locations.models import Location
from search.search_index import PostIndex
from tinymce.models import HTMLField
from users.models import User


# 파일 이름이 겹치지 않도록 현재 시각을 기반으로 파일 경로를 생성하는 함수
def image_upload_path(instance, filename):
    # 현재 시각을 'YYYYMMDD_HHMMSS' 형식으로 문자열화
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    # 고유한 파일 경로를 생성하여 반환
    return f"{timestamp}_{filename}"


# 게시물(Post) 모델 정의
class Post(models.Model):
    # 작성자 (User 모델과 외래키 관계)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    # 게시물 제목
    title = models.CharField(max_length=200, null=False)
    # 태그 (옵션 필드)
    tag = models.CharField(max_length=200, null=True, blank=True)
    # 게시물 위치 (Location 모델과 외래키 관계)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="posts"
    )
    # 게시물 본문 (HTML 형식으로 저장)
    body = HTMLField()
    # 게시물 생성 시각 (자동으로 현재 시각으로 설정)
    created_at = models.DateTimeField(auto_now_add=True)
    # 게시물 수정 시각 (자동으로 현재 시각으로 업데이트)
    updated_at = models.DateTimeField(auto_now=True)
    # 조회수 (기본값: 0)
    view_count = models.PositiveIntegerField(default=0)
    # 여행 시작 날짜 (옵션 필드)
    travel_start_date = models.DateField(null=True, blank=True)
    # 여행 종료 날짜 (옵션 필드)
    travel_end_date = models.DateField(null=True, blank=True)
    # 썸네일 이미지 (옵션 필드)
    thumbnail = models.ImageField(upload_to=image_upload_path, null=True, blank=True)

    def __str__(self):
        return self.title  # 게시물의 제목을 문자열로 반환

    # 게시물 인덱싱 메서드 (검색 엔진용)
    def indexing(self):
        # Elasticsearch와 같은 검색 엔진에 저장할 인덱스 객체 생성
        obj = PostIndex(
            meta={"id": self.id},
            user_id=self.user_id.id,
            title=self.title,
            content=self.body,
            thumbnail=self.thumbnail.url if self.thumbnail else "",
            created_at=self.created_at,
        )
        obj.save()  # 인덱스 저장
        return obj.to_dict(include_meta=True)  # 저장된 인덱스를 사전 형식으로 반환


# 이미지(Image) 모델 정의
# 게시물(Post)과 외래키 관계이며, 게시물 생성 전에 이미지를 로드할 수 있도록 board 필드가 null을 허용
class Image(models.Model):
    # 게시물 (외래키, null 허용)
    board = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images", null=True, blank=True
    )
    # 이미지 파일
    image = models.ImageField(upload_to=image_upload_path)
    # 이미지 생성 시각 (자동으로 현재 시각으로 설정)
    created_at = models.DateTimeField(auto_now_add=True)


# 댓글(Comment) 모델 정의
class Comment(models.Model):
    # 댓글이 달린 게시물 (Post 모델과 외래키 관계)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    # 작성자 (User 모델과 외래키 관계)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # 댓글 내용
    content = models.TextField()
    # 댓글 작성 시각 (자동으로 현재 시각으로 설정)
    created_at = models.DateTimeField(auto_now_add=True)
    # 댓글 수정 시각 (자동으로 현재 시각으로 업데이트)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content  # 댓글 내용을 문자열로 반환


# 좋아요(Like) 모델 정의
class Like(models.Model):
    # 좋아요를 한 사용자 (User 모델과 외래키 관계)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 좋아요가 눌린 게시물 (Post 모델과 외래키 관계)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # 좋아요 생성 시각 (자동으로 현재 시각으로 설정)
    created_at = models.DateTimeField(auto_now_add=True)

    # 사용자와 게시물의 조합이 유일해야 함을 정의
    class Meta:
        unique_together = ("user", "post")
