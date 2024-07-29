from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Location, LocationImage


class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 1


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location_id", "city", "l_category")
    inlines = [LocationImageInline]
    fields = (
        "location_id",
        "city",
        "popular_cities",
        "description",
        "highlights",
        "l_category",
    )
    search_fields = ("city", "description", "l_category")


@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("location", "image_url")


@receiver(post_save, sender=LocationImage)
def update_image_url(sender, instance, **kwargs):
    if not instance.image_url:
        instance.image_url = instance.image.url
        instance.save()
