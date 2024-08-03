from django.conf import settings
from django.core.management.base import BaseCommand
from locations.models import LocationImage
from locations.utils import (
    upload_image_to_s3,
)  # S3에 이미지를 업로드하는 유틸리티 함수 가져오기


# 이 커맨드는 이미지 파일을 S3에 업로드하고, 데이터베이스의 이미지 URL을 업데이트하는 역할을 합니다.
class Command(BaseCommand):
    help = "Upload images to S3 and update the URLs in the database"  # 커맨드의 설명

    def handle(self, *args, **kwargs):
        # 모든 LocationImage 객체를 가져옵니다.
        images = LocationImage.objects.all()

        # 각 이미지에 대해 S3에 업로드하고 URL을 업데이트하는 작업 수행
        for image in images:
            try:
                # S3에 저장될 이미지 경로 설정 (도시 이름과 이미지 ID를 포함)
                s3_path = f"locations/{image.location.city}/{image.id}.jpg"  # 이미지 형식에 맞게 설정

                # S3에 이미지를 업로드하고 반환된 URL을 데이터베이스에 저장
                s3_url = upload_image_to_s3(
                    image.image_url, settings.AWS_STORAGE_BUCKET_NAME, s3_path
                )

                # 이미지의 URL 필드를 S3 URL로 업데이트하고 저장
                image.image_url = s3_url
                image.save()

                # 성공 메시지를 출력
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully updated image URL for {image.id}")
                )
            except Exception as e:
                # 예외 발생 시 오류 메시지를 출력
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to update image URL for {image.id}: {str(e)}"
                    )
                )
