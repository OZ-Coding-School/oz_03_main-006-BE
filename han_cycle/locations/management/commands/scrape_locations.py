import os

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from locations.models import Location, LocationImage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Command(BaseCommand):
    help = "스크래핑을 통해 네이버 여행에서 도시 정보를 가져옵니다."

    def handle(self, *args, **kwargs):
        self.scrape_city_info()

    def click_icon(self, driver):
        driver.get("https://travel.naver.com/domestic")
        time.sleep(1)
        try:
            element = driver.find_element(By.CSS_SELECTOR, "a.header_search__4UCHI")
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
        except Exception as e:
            print("버튼 못찾아따")
            print(e)

    def click_button_by_class(self, driver):
        parent_element = driver.find_element(
            By.CLASS_NAME, "searchbox_home_tabs__FA2_B"
        )
        elements = parent_element.find_elements(
            By.CLASS_NAME, "searchbox_home_tab__RNL7F"
        )
        for element in elements:
            element.click()
            time.sleep(1)
            button = driver.find_element(By.CLASS_NAME, "searchbox_home_button__hVBDW")
            button.click()
            time.sleep(1)

    def scrape_city_info(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")

        os.environ["WDM_LOCAL"] = "/tmp/.wdm"
        driver_path = ChromeDriverManager().install()
        print(driver_path)
        driver = webdriver.Chrome(executable_path=driver_path, options=options)

        self.click_icon(driver)
        self.click_button_by_class(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")

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

        for city_id, city_name in CITIES.items():
            city_link = soup.find("a", string=city_name)
            if not city_link:
                print(f"City link not found for: {city_name}")
                continue

            city_url = "https://travel.naver.com" + city_link["href"]
            city_response = requests.get(city_url)
            city_soup = BeautifulSoup(city_response.text, "html.parser")

            popular_cities_elements = city_soup.select(".cityInfo_anchor__wk6Cu")
            if popular_cities_elements:
                popular_cities = ", ".join(
                    [elem.text.strip() for elem in popular_cities_elements]
                )
            else:
                print(f"Popular cities elements not found for: {city_name}")
                popular_cities = ""

            description_element = city_soup.select_one(".description")
            if description_element:
                description = description_element.text.strip()
            else:
                print(f"Description element not found for: {city_name}")
                description = ""

            highlights_element = city_soup.select_one(".highlights")
            if highlights_element:
                highlights = ", ".join(
                    [tag.text.strip() for tag in highlights_element.find_all("span")]
                )
            else:
                print(f"Highlights element not found for: {city_name}")
                highlights = ""

            location, created = Location.objects.update_or_create(
                city=city_name,
                defaults={
                    "popular_cities": popular_cities,
                    "description": description,
                    "highlights": highlights,
                },
            )

            image_elements = city_soup.select(".image img")
            for img in image_elements[:5]:
                image_url = img["src"]
                LocationImage.objects.update_or_create(
                    location=location, image_url=image_url
                )

            print(
                f"Scraped data for {city_name}: popular_cities={popular_cities}, description={description}, highlights={highlights}"
            )

        driver.quit()
