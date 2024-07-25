from django.core.management.base import BaseCommand
from locations.scraper import scrape_city_info

class Command(BaseCommand):
    help = "스크래핑을 통해 도시 정보를 가져옵니다."

    def handle(self, *args, **options):
        # 스크래핑 함수 실행
        scrape_city_info()
        self.stdout.write(self.style.SUCCESS("Successfully scraped city information"))