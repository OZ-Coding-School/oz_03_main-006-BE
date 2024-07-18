from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    provider = models.CharField(max_length=20, null=False)  # 'google', 'kakao', 'naver', 'email'
    social_id = models.CharField(max_length=100, null=True, blank=True)  # 소셜 로그인 ID
    nickname = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['provider', 'social_id'], name='unique_provider_social_id')
        ]

    def __str__(self):
        return self.nickname

class Location(models.Model):
    city = models.CharField(max_length=100, null=False)
    district = models.CharField(max_length=100, null=False)
    symbol = models.CharField(max_length=100, blank=True)
    population = models.IntegerField(blank=True, null=True)
    information = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    image_url = models.URLField(null=True, blank=True) # 지역 이미지
    popular_cities = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # highlights = models.CharField(max_length=200, blank=True) # 하이라이트 추가 논의 중
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, null=False)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['-view_count']), # 조회수 역순 인덱스
        ]

    def __str__(self):
        return self.title

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    is_representative = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=100, null=True, blank=True)
    introduction = models.TextField(blank=True)


# class ProfileImage(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_images')
#     image_url = models.URLField(null=False)
#     is_active = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['user', 'is_active'])  # 사용자별 활성 이미지 빠른 조회
#         ]

class Weather(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_set')  # ForeignKey로 변경
    base_date = models.DateField()
    base_time = models.TimeField()
    fcst_date = models.DateField()
    category = models.CharField(max_length=10)  # POP, SKY, TMN, TMX
    fcst_value = models.CharField(max_length=20)

    class Meta:
        unique_together = ('location', 'base_date', 'base_time', 'fcst_date', 'category')

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'tag')

class PostLocation(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_locations')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'location')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)

class LocationCategory(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('location', 'category')
