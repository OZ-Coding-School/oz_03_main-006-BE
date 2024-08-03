from boards.models import Post
from django.core.management.base import BaseCommand
from locations.models import Location
from users.models import User


# 커스텀 관리 명령어 정의
class Command(BaseCommand):
    help = "Reindex all models to Elasticsearch"  # 명령어에 대한 간단한 설명

    def handle(self, *args, **kwargs):
        """
        이 메서드는 'python manage.py reindex' 명령어가 실행될 때 호출됩니다.
        전체 모델에 대해 색인 작업을 수행합니다.
        """
        self.reindex_posts()  # 게시물(Post) 모델 색인
        self.reindex_locations()  # 위치(Location) 모델 색인
        self.reindex_users()  # 사용자(User) 모델 색인
        self.stdout.write(
            self.style.SUCCESS("Successfully reindexed all models.")
        )  # 성공 메시지 출력

    def reindex_posts(self):
        """
        모든 게시물(Post) 데이터를 Elasticsearch에 색인합니다.
        """
        for post in Post.objects.all():
            post.indexing()  # 각 게시물에 대해 색인 작업 수행

    def reindex_locations(self):
        """
        모든 위치(Location) 데이터를 Elasticsearch에 색인합니다.
        """
        for location in Location.objects.all():
            location.indexing()  # 각 위치에 대해 색인 작업 수행

    def reindex_users(self):
        """
        모든 사용자(User) 데이터를 Elasticsearch에 색인합니다.
        """
        for user in User.objects.all():
            user.indexing()  # 각 사용자에 대해 색인 작업 수행
