from django.db import models
from locations.models import Location


class Weather(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="weather_set"
    )
    base_date = models.DateField(null=False)  # 발표 일자
    base_time = models.TimeField(null=False)  # 발표 시각
    fcst_date = models.DateField(null=False)  # 예보 날짜
    category = models.CharField(max_length=10, null=False)  # POP, SKY, TMN, TMX
    fcst_value = models.CharField(max_length=20, null=False)  # 예보데이터 저장 필드

    class Meta:
        unique_together = (
            "location",
            "base_date",
            "base_time",
            "fcst_date",
            "category",
        )
        indexes = [
            models.Index(
                fields=["location", "fcst_date"]
            ),  # 지역 및 예보 날짜 기준 검색
        ]
