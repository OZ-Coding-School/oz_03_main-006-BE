# from datetime import datetime, timedelta, timezone

# import requests
# from bs4 import BeautifulSoup
# from celery import shared_task
# from django.conf import settings
# from locations.models import Location  # Location 모델 import

# from .models import Weather

# logger = logging.getLogger(__name__)


# @shared_task
# def scrape_weather_data():
#     service_key = settings.KOREA_WEATHER_API_KEY  # 기상청 API 서비스 키
#     base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
#     target_categories = ["POP", "SKY", "TMN", "TMX"]
#     # 강수확률 POP, 하늘상태 SKY, 최저기온 TMN, 최고기온 TMX

#     # 현재 시간(KST) 기준으로 base_date, base_time 설정
#     now = datetime.now(timezone.utc) + timedelta(hours=9)  # KST로 변환
#     base_date = now.strftime("%Y%m%d")
#     base_time = "0200"  # 02시 예보 기준

#     # 지역 목록 (ID와 매핑)
#     location_codes = {
#         1: {"nx": 60, "ny": 127},  # 서울
#         2: {"nx": 60, "ny": 120},  # 경기도
#         3: {"nx": 55, "ny": 124},  # 인천
#         4: {"nx": 73, "ny": 134},  # 강원도
#         5: {"nx": 87, "ny": 106},  # 경상북도
#         6: {"nx": 91, "ny": 77},  # 경상남도
#         7: {"nx": 89, "ny": 90},  # 대구
#         8: {"nx": 102, "ny": 84},  # 울산
#         9: {"nx": 98, "ny": 76},  # 부산
#         10: {"nx": 69, "ny": 107},  # 충청북도
#         11: {"nx": 68, "ny": 100},  # 충청남도
#         12: {"nx": 66, "ny": 103},  # 세종
#         13: {"nx": 67, "ny": 100},  # 대전
#         14: {"nx": 63, "ny": 89},  # 전라북도
#         15: {"nx": 51, "ny": 67},  # 전라남도
#         16: {"nx": 58, "ny": 74},  # 광주
#         17: {"nx": 52, "ny": 38},  # 제주도
#     }

#     for location_id, coords in location_codes.items():
#         nx = coords["nx"]
#         ny = coords["ny"]
#         params = {
#             "serviceKey": service_key,
#             "pageNo": 1,
#             "numOfRows": 1000,  # 필요한 만큼 늘려서 설정
#             "dataType": "JSON",
#             "base_date": base_date,
#             "base_time": base_time,
#             "nx": nx,
#             "ny": ny,
#         }

#         try:
#             response = requests.get(base_url, params=params)
#             response.raise_for_status()

#             data = response.json()
#             for item in data["response"]["body"]["items"]["item"]:
#                 fcst_date = item["fcstDate"]
#                 fcst_time = item["fcstTime"]
#                 W_category = item["category"]
#                 fcst_value = item["fcstValue"]

#                 # 오늘 날짜 예보만 저장
#                 if fcst_date == base_date:
#                     Weather.objects.update_or_create(
#                         location_id=location_id,  # 지역 ID 사용
#                         base_date=base_date,
#                         base_time=base_time,
#                         fcst_date=fcst_date,
#                         W_category=W_category,
#                         defaults={"fcst_value": fcst_value},
#                     )

#             location = Location.objects.get(
#                 location_id=location_id
#             )  # Location 객체 가져오기
#             logger.info(f"{location.city} {location.district} 날씨 정보 스크래핑 완료")
#         except Location.DoesNotExist:
#             logger.error(f"Location ID {location_id}에 해당하는 지역 정보가 없습니다.")
#         except Exception as e:
#             logger.error(
#                 f"{location.city} {location.district} 날씨 정보 스크래핑 중 오류 발생: {e}"
#             )
