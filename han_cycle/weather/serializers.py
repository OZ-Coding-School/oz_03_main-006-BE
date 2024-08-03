from rest_framework import serializers

from .models import Weather


# Weather 모델을 직렬화하는 클래스입니다.
class WeatherSerializer(serializers.ModelSerializer):
    # sky_status는 모델의 메서드를 통해 계산된 값을 포함하는 필드입니다.
    sky_status = serializers.SerializerMethodField()

    class Meta:
        model = Weather  # 직렬화할 모델을 지정
        fields = [
            "location",  # 위치 정보 (외래키)
            "base_date",  # 기준 날짜
            "fcst_date",  # 예보 날짜
            "base_time",  # 기준 시간
            "POP",  # 강수확률
            "TMN",  # 최저 기온
            "TMX",  # 최고 기온
            "SKY",  # 하늘 상태 코드
            "sky_status",  # 하늘 상태의 의미를 나타내는 추가 필드
        ]

    # sky_status 필드에 대한 값을 반환하는 메서드입니다.
    def get_sky_status(self, obj):
        # Weather 모델의 get_sky_status() 메서드를 호출하여 값을 반환합니다.
        return obj.get_sky_status()
