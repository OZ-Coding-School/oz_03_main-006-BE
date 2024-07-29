from django.core.management.base import BaseCommand
from boards.models import Post
from locations.models import Location
from users.models import User

class Command(BaseCommand):
    help = 'Reindex all models to Elasticsearch'

    def handle(self, *args, **kwargs):
        self.reindex_posts()
        self.reindex_locations()
        self.reindex_users()
        self.stdout.write(self.style.SUCCESS('Successfully reindexed all models.'))

    def reindex_posts(self):
        for post in Post.objects.all():
            post.indexing()

    def reindex_locations(self):
        for location in Location.objects.all():
            location.indexing()

    def reindex_users(self):
        for user in User.objects.all():
            user.indexing()