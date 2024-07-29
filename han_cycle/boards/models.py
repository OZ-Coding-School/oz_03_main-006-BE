from django.db import models
from django.utils import timezone
from locations.models import Location
from tinymce.models import HTMLField
from users.models import User


# 파일이름 겹치지 않도록 설정해주는 함수
def image_upload_path(instance, filename):
    timestamp = timezone.now().strftime(
        "%Y%m%d_%H%M%S"
    )  # 현재 시각을 이용하여 고유한 시간 기반 문자열 생성
    return f"{timestamp}_{filename}"


# 게시물 model
class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    region = models.IntegerField(default=0)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )  # Location 외래 키 추가
    body = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to=image_upload_path, null=True, blank=True)

    def __str__(self):
        return self.title


# 이미지 모델, 게시물 post전 이미지를 로드해야하기 때문에 board값이 null이어도 허용할 수 있도록 함
class Image(models.Model):
    board = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images", null=True, blank=True
    )
    image = models.ImageField(upload_to=image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)


# 댓글 모델
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # 사용자와 게시물의 조합은 유일해야 함
    class Meta:
        unique_together = ("user", "post")
