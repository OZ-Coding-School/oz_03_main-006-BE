import requests
from bs4 import BeautifulSoup
from .models import Location, LocationImage

def scrape_city_info():
    # 네이버 여행 국내 페이지 URL 설정
    url = "https://travel.naver.com/domestic"
    response = requests.get(url)  # 페이지 요청
    soup = BeautifulSoup(response.text, "html.parser")  # BeautifulSoup 객체 생성

    # 도시 ID와 이름 매핑
    CITIES = {
        1: "서울",
        2: "경기도",
        3: "인천",
        4: "강원도",
        5: "경상북도",
        6: "경상남도",
        7: "대구",
        8: "울산",
        9: "부산",
        10: "충청북도",
        11: "충청남도",
        12: "세종",
        13: "대전",
        14: "전라북도",
        15: "전라남도",
        16: "광주",
        17: "제주도",
    }

    # 각 도시별로 스크래핑 수행
    for city_id, city_name in CITIES.items():
        # 각 도시 섹션 찾기
        city_section = soup.find("section", {"data-name": city_name})
        if not city_section:
            print(f"City section not found for: {city_name}")
            continue  # 도시 섹션이 없으면 건너뛰기

        # 인기도시 요소들 찾기
        popular_cities_elements = city_section.select(".cityInfo_anchor__wk6Cu")
        if popular_cities_elements:
            popular_cities = ", ".join([elem.text.strip() for elem in popular_cities_elements])
        else:
            print(f"Popular cities elements not found for: {city_name}")
            popular_cities = ""

        # 도시 설명 요소 찾기
        description_element = city_section.select_one(".description")
        if description_element:
            description = description_element.text.strip()
        else:
            print(f"Description element not found for: {city_name}")
            description = ""

        # 하이라이트 요소 찾기
        highlights_element = city_section.select_one(".highlights")
        if highlights_element:
            highlights = ", ".join([tag.text.strip() for tag in highlights_element.find_all("span")])
        else:
            print(f"Highlights element not found for: {city_name}")
            highlights = ""

        # Location 객체 업데이트 또는 생성
        location, created = Location.objects.update_or_create(
            city=city_name,
            defaults={
                "popular_cities": popular_cities,
                "description": description,
                "highlights": highlights,
            },
        )

        # 이미지 요소들 찾기
        image_elements = city_section.select(".image img")
        for img in image_elements[:5]:  # 가져올 이미지 개수 제한
            image_url = img["src"]
            # LocationImage 객체 업데이트 또는 생성
            LocationImage.objects.update_or_create(
                location=location,
                image_url=image_url
            )

        # 스크래핑된 데이터 출력
        print(f"Scraped data for {city_name}: popular_cities={popular_cities}, description={description}, highlights={highlights}")