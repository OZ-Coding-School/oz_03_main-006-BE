# locations/management/commands/update_image_urls.py

from django.conf import settings
from django.core.management.base import BaseCommand
from locations.models import LocationImage
from locations.utils import upload_image_to_s3  # utils 파일에서 함수 가져오기


class Command(BaseCommand):
    help = "Upload images to S3 and update the URLs in the database"

    def handle(self, *args, **kwargs):
        images = LocationImage.objects.all()
        for image in images:
            try:
                s3_path = f"locations/{image.location.city}/{image.id}.jpg"  # 이미지 형식에 맞게 설정
                s3_url = upload_image_to_s3(
                    image.image_url, settings.AWS_STORAGE_BUCKET_NAME, s3_path
                )
                image.image_url = s3_url
                image.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully updated image URL for {image.id}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to update image URL for {image.id}: {str(e)}"
                    )
                )
