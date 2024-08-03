from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Location, LocationImage


# LocationImage를 LocationAdmin에서 인라인으로 표시하기 위한 설정
class LocationImageInline(admin.TabularInline):
    model = LocationImage  # 인라인으로 표시할 모델을 지정
    extra = 1  # 빈 필드 추가 개수 (새로운 LocationImage를 추가할 수 있는 필드)


# Location 모델을 관리하기 위한 관리자(admin) 클래스 정의
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location_id", "city", "l_category")  # 관리자 화면에 표시할 필드
    inlines = [LocationImageInline]  # LocationImage를 인라인으로 추가
    fields = (
        "location_id",
        "city",
        "popular_cities",
        "description",
        "highlights",
        "l_category",
    )  # 관리자 폼에서 편집할 수 있는 필드 목록
    search_fields = ("city", "description", "l_category")  # 검색 필드 설정


# LocationImage 모델을 관리하기 위한 관리자(admin) 클래스 정의
@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("location", "image_url")  # 관리자 화면에 표시할 필드


# LocationImage 모델이 저장될 때 image_url 필드를 자동으로 업데이트하기 위한 신호 수신기
@receiver(post_save, sender=LocationImage)
def update_image_url(sender, instance, **kwargs):
    if not instance.image_url:
        # image_url 필드가 비어있다면 image 필드의 URL을 사용하여 업데이트
        instance.image_url = instance.image.url
        instance.save()
