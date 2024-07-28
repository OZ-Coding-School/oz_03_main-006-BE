from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from locations.models import Location
from weather.models import Weather


class Command(BaseCommand):
    help = "Fetch weather data from the Korean Meteorological Administration API"

    def handle(self, *args, **kwargs):
        location_codes = {
            1: {"nx": 60, "ny": 127},  # 서울
            2: {"nx": 60, "ny": 120},  # 경기도
            3: {"nx": 55, "ny": 124},  # 인천
            4: {"nx": 73, "ny": 134},  # 강원도
            5: {"nx": 87, "ny": 106},  # 경상북도
            6: {"nx": 91, "ny": 77},  # 경상남도
            7: {"nx": 89, "ny": 90},  # 대구
            8: {"nx": 102, "ny": 84},  # 울산
            9: {"nx": 98, "ny": 76},  # 부산
            10: {"nx": 69, "ny": 107},  # 충청북도
            11: {"nx": 68, "ny": 100},  # 충청남도
            12: {"nx": 66, "ny": 103},  # 세종
            13: {"nx": 67, "ny": 100},  # 대전
            14: {"nx": 63, "ny": 89},  # 전라북도
            15: {"nx": 51, "ny": 67},  # 전라남도
            16: {"nx": 58, "ny": 74},  # 광주
            17: {"nx": 52, "ny": 38},  # 제주도
        }

        base_date = datetime.now().strftime("%Y%m%d")
        base_time = "0500"  # 기본 발표 시각

        service_key = settings.KMA_API_KEY  # 기상청 공공 API 키를 settings.py에 추가

        for location_id, coords in location_codes.items():
            location = Location.objects.get(pk=location_id)
            nx, ny = coords["nx"], coords["ny"]

            url = (
                f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
                f"?serviceKey={service_key}&numOfRows=100&pageNo=1&dataType=JSON"
                f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
            )

            response = requests.get(url)
            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch data: {response.status_code}")
                )
                self.stdout.write(
                    self.style.ERROR(f"Response content: {response.content}")
                )
                continue

            try:
                data = response.json()
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f"JSON decode error: {e}"))
                self.stdout.write(
                    self.style.ERROR(f"Response content: {response.content}")
                )
                continue

            if data["response"]["header"]["resultCode"] == "00":
                items = data["response"]["body"]["items"]["item"]

                for item in items:
                    fcst_date = item["fcstDate"]
                    fcst_time = item["fcstTime"]
                    category = item["category"]
                    fcst_value = item["fcstValue"]

                    # 기존 데이터베이스의 데이터를 업데이트하거나 새로운 데이터를 생성합니다.
                    weather, created = Weather.objects.update_or_create(
                        location=location,
                        base_date=base_date,
                        fcst_date=fcst_date,
                        base_time=fcst_time,
                        defaults={
                            category: fcst_value,
                        },
                    )

                    # fcst_value는 항상 최신 값으로 유지합니다.
                    if not created:
                        setattr(weather, category, fcst_value)
                        weather.fcst_value = fcst_value
                        weather.save()

                    # Debug 용 출력
                    print(
                        f"Location: {location.city}, Date: {fcst_date}, Time: {fcst_time}, Category: {category}, Value: {fcst_value}"
                    )

            else:
                self.stdout.write(self.style.ERROR("Failed to fetch data from API"))
