from django.db import models


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
    city = models.CharField(max_length=100, null=False)
    popular_cities = models.TextField(blank=True)
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True)  # 쉼표로 구분된 문자열


class L_Category(models.Model):
    name = models.CharField(max_length=50, unique=True, null=False)


class LocationCategory(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    L_category = models.ForeignKey(L_Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("location", "L_category")


class LocationImage(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField(max_length=200)
