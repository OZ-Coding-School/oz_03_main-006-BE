from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField 
from users.models import User


#파일이름 겹치지 않도록 설정해주는 함수
def image_upload_path(instance, filename):
    # filename은 업로드된 파일의 이름입니다.
    #post_id = instance.board.id
    #is_representative = "representative" if instance.is_representative else "not_representative"
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')  # 현재 시각을 이용하여 고유한 시간 기반 문자열 생성
    return f'images/{timestamp}_{filename}'

class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    region = models.IntegerField(default=1)
    body = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)
    thumbnail=models.ImageField(upload_to='image_upload_path')

    def __str__(self):
        return self.title
    
class Image(models.Model):
    board = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='image_upload_path')
    is_representative = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.content

    
