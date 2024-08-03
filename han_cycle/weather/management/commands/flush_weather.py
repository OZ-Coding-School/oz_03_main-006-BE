from django.core.management.base import BaseCommand
from weather.models import Weather


# 이 커맨드는 모든 날씨 데이터를 삭제하는 데 사용됩니다.
class Command(BaseCommand):
    help = "Delete all weather data"  # 관리 명령의 도움말 설명

    def handle(self, *args, **kwargs):
        # Weather 모델에 저장된 모든 날씨 데이터를 삭제합니다.
        Weather.objects.all().delete()

        # 모든 데이터를 성공적으로 삭제했음을 출력합니다.
        self.stdout.write(self.style.SUCCESS("Successfully deleted all weather data"))
