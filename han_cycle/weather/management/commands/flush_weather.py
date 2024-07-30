from django.core.management.base import BaseCommand
from weather.models import Weather


class Command(BaseCommand):
    help = "Delete all weather data"

    def handle(self, *args, **kwargs):
        Weather.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted all weather data"))
