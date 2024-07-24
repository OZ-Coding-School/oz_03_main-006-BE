from django.urls import path
from .views import *


urlpatterns = [
    path('',posts),
    path('<int:pk>',post_detail, name="post"),
    path('<int:pk>/comments', comment_create),
    path('comments/<int:comment_pk>',comment_detail),
    path('images',upload_image),
]