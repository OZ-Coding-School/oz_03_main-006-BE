from boards.models import Post
from django.core.management.base import BaseCommand
from locations.models import Location
from search.search_indexes import LocationIndex, PostIndex, UserIndex
from users.models import User


class Command(BaseCommand):
    help = "Index all data to Elasticsearch"

    def handle(self, *args, **kwargs):
        self.index_posts()
        self.index_users()
        self.index_locations()

    def index_posts(self):
        posts = Post.objects.all()
        for post in posts:
            post_index = PostIndex(
                meta={"id": post.id},
                title=post.title,
                content=post.body,
                created_at=post.created_at,
            )
            post_index.save()
        self.stdout.write(self.style.SUCCESS("Successfully indexed posts"))

    def index_users(self):
        users = User.objects.all()
        for user in users:
            user_index = UserIndex(
                meta={"id": user.id},
                nickname=user.nickname,
                email=user.email,
            )
            user_index.save()
        self.stdout.write(self.style.SUCCESS("Successfully indexed users"))

    def index_locations(self):
        locations = Location.objects.all()
        for location in locations:
            location_index = LocationIndex(
                meta={"id": location.id},
                city=location.city,
                description=location.description,
                highlights=location.highlights,
            )
            location_index.save()
        self.stdout.write(self.style.SUCCESS("Successfully indexed locations"))
