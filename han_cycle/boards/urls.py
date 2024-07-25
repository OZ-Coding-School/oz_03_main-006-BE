from django.urls import path

from .views import *

urlpatterns = [
    path("posts/", posts, name="posts"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("comments/", CommentListView.as_view(), name="comment_list"),
    path(
        "posts/<int:pk>/comments/", CommentCreateView.as_view(), name="comment_create"
    ),
    path(
        "comments/<int:comment_pk>/", CommentDetailView.as_view(), name="comment_detail"
    ),
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
    path("posts/<int:pk>/like/", LikeView.as_view(), name="click_like"),
]
