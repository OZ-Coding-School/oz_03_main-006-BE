from django.contrib import admin

from .models import L_Category, Location, LocationCategory, LocationImage


class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 1


class LocationCategoryInline(admin.TabularInline):
    model = LocationCategory
    extra = 1


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location_id", "city")
    inlines = [LocationImageInline, LocationCategoryInline]
    fields = ("location_id", "city", "popular_cities", "description", "highlights")
    search_fields = ("city", "description")


@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ("location", "image_url")


@admin.register(L_Category)
class LCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(LocationCategory)
class LocationCategoryAdmin(admin.ModelAdmin):
    list_display = ("location", "L_category")
