from django.db import models
from locations.models import Location


class Weather(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    base_date = models.CharField(max_length=8)  # 예보 발표 날짜
    fcst_date = models.CharField(max_length=8)  # 예보 대상 날짜
    base_time = models.CharField(max_length=4)  # 예보 발표 시각
    POP = models.FloatField(null=True)  # 강수확률 (실수로 변경)
    TMP = models.FloatField(null=True)  # 1시간 기온 (실수)
    SKY = models.IntegerField(null=True)  # 하늘상태 (정수)

    class Meta:
        unique_together = ("location", "fcst_date", "base_time")

    def __str__(self):
        return f"{self.location} - {self.fcst_date} {self.base_time} - POP: {self.POP}, TMP: {self.TMP}, SKY: {self.SKY}"

    def get_sky_status(self):
        if 0 <= self.SKY <= 5:
            return "맑음"
        elif 6 <= self.SKY <= 8:
            return "구름많음"
        elif 9 <= self.SKY <= 10:
            return "흐림"
        else:
            return "알 수 없음"
