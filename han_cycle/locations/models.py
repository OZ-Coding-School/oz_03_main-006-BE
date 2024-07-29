from django.db import models
from search.search_index import LocationIndex


class Location(models.Model):
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
    location_id = models.IntegerField(choices=CITY_CHOICES, primary_key=True)
    l_category = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, null=False)
    popular_cities = models.TextField(blank=True)
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True)  # 쉼표로 구분된 문자열

    def __str__(self):
        return self.city

    def indexing(self):
        obj = LocationIndex(
            meta={"id": self.location_id},
            city=self.city,
            description=self.description,
            highlights=self.highlights,
        )
        obj.save()
        return obj.to_dict(include_meta=True)


class LocationImage(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField(max_length=200)

    def __str__(self):
        return self.image_url
