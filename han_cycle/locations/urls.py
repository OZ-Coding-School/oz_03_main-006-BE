from django.urls import path

from .views import (
    HighlightListView,
    LocationDetailView,
    LocationHighlightDetailView,
    LocationImagesView,
    LocationListView,
)

# location 앱의 URL 패턴 정의
urlpatterns = [
    # 모든 Location 객체의 목록을 가져오는 URL 패턴
    path("", LocationListView.as_view(), name="location-list"),
    # 특정 Location 객체의 세부 정보를 가져오는 URL 패턴
    path("<int:pk>/", LocationDetailView.as_view(), name="location-detail"),
    # 모든 Location 객체의 하이라이트 목록을 가져오는 URL 패턴
    path("highlights/", HighlightListView.as_view(), name="locations_highlights"),
    # 특정 Location 객체의 하이라이트 세부 정보를 가져오는 URL 패턴
    path(
        "<int:location_id>/highlight/",
        LocationHighlightDetailView.as_view(),
        name="location_highlight_detail",
    ),
    # 특정 Location 객체의 이미지 목록을 가져오는 URL 패턴
    path(
        "<location_id>/images/",
        LocationImagesView.as_view(),
        name="location-images",
    ),
]
