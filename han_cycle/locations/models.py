from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from search.search_index import LocationIndex


# Location 모델: 특정 도시나 지역에 대한 정보를 저장하는 모델입니다.
class Location(models.Model):
    # 도시 선택을 위한 선택지 (CITY_CHOICES)
    CITY_CHOICES = [
        (1, "서울"),
        (2, "경기도"),
        (3, "인천"),
        (4, "강원도"),
        (5, "경상북도"),
        (6, "경상남도"),
        (7, "대구"),
        (8, "울산"),
        (9, "부산"),
        (10, "충청북도"),
        (11, "충청남도"),
        (12, "세종"),
        (13, "대전"),
        (14, "전라북도"),
        (15, "전라남도"),
        (16, "광주"),
        (17, "제주도"),
    ]
    # 도시 ID (기본 키)
    location_id = models.IntegerField(choices=CITY_CHOICES, primary_key=True)
    # 지역 카테고리 (옵션)
    l_category = models.CharField(max_length=100, blank=True, null=True)
    # 도시 이름
    city = models.CharField(max_length=100, null=False)
    # 인기 있는 도시 목록
    popular_cities = models.TextField(blank=True)
    # 도시 설명
    description = models.TextField(blank=True)
    # 주요 하이라이트 (쉼표로 구분된 문자열)
    highlights = models.TextField(blank=True)

    def __str__(self):
        return self.city  # 도시 이름을 문자열로 반환

    # 이 메서드는 해당 Location 객체를 검색 인덱싱하는 데 사용됩니다.
    def indexing(self):
        obj = LocationIndex(
            meta={"id": self.location_id},
            city=self.city,
            description=self.description,
            highlights=self.highlights,
        )
        obj.save()
        return obj.to_dict(include_meta=True)


# LocationImage 모델: 특정 Location에 연관된 이미지 정보를 저장하는 모델입니다.
class LocationImage(models.Model):
    # Location 모델과의 외래키 관계
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="images"
    )
    # 이미지 필드 (S3에 저장)
    image = models.ImageField(upload_to="locations/")
    # 이미지 URL 필드
    image_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.location.city} - Image"  # 도시 이름과 이미지를 문자열로 반환


# LocationImage 객체가 저장된 후 image_url 필드를 자동으로 업데이트하는 신호 수신기
@receiver(post_save, sender=LocationImage)
def update_image_url(sender, instance, **kwargs):
    if not instance.image_url:
        # image_url 필드가 비어 있을 경우, image 필드의 URL로 채웁니다.
        instance.image_url = instance.image.url
        instance.save()
