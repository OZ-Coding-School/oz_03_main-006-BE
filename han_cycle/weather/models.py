from django.db import models
from locations.models import Location


class Weather(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    base_date = models.CharField(max_length=8)  # 예보 발표 날짜
    fcst_date = models.CharField(max_length=8)  # 예보 대상 날짜
    base_time = models.CharField(max_length=4)  # 예보 발표 시각
    POP = models.IntegerField(null=True)  # 강수확률
    TMX = models.IntegerField(null=True)  # 일 최고기온
    TMN = models.IntegerField(null=True)  # 일 최저기온
    SKY = models.IntegerField(null=True)  # 하늘상태
    fcst_value = models.CharField(max_length=10)  # 예보 데이터 저장 필드

    class Meta:
        unique_together = ("location", "fcst_date", "base_time")

    def __str__(self):
        return f"{self.location} - {self.fcst_date} {self.base_time} - POP: {self.POP}, TMX: {self.TMX}, TMN: {self.TMN}, SKY: {self.SKY}"
