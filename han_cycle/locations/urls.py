from django.urls import path

from .views import (
    HighlightListView,
    LocationDetailView,
    LocationHighlightDetailView,
    LocationListView,
)

urlpatterns = [
    path("", LocationListView.as_view(), name="location-list"),
    path("<int:pk>/", LocationDetailView.as_view(), name="location-detail"),
    path("highlights/", HighlightListView.as_view(), name="locations_highlights"),
    path(
        "<int:location_id>/highlight/",
        LocationHighlightDetailView.as_view(),
        name="location_highlight_detail",
    ),
]
