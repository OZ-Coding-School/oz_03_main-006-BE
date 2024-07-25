from django.urls import path
from . import views

urlpatterns = [
    path('scrape/', views.scrape_location_data, name='scrape_location_data'),  # 스크래핑 엔드포인트
    path('', views.LocationListView.as_view(), name='location_list'),  # 모든 위치 정보 조회 엔드포인트
    path('<int:pk>/', views.LocationDetailView.as_view(), name='location_detail'),  # 특정 위치 정보 조회 엔드포인트
    path('<int:pk>/highlights/', views.HighlightView.as_view(), name='location_highlights'),  # 하이라이트 정보 조회 엔드포인트
]