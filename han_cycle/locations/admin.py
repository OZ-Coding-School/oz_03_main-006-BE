from django.contrib import admin

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
    )  # L_category 추가
    search_fields = ("city", "description", "l_category")


@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("location", "image_url")
