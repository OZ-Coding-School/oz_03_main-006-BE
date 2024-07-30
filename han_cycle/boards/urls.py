from django.urls import path

from .views import (
    CommentCreateView,
    CommentDetailView,
    CommentListView,
    GetUserPost,
    LikeView,
    PostDetailView,
    PostsByLocationView,
    UploadImageView,
    posts,
)

# 새 뷰 추가

urlpatterns = [
    path("", posts, name="posts"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("comments/", CommentListView.as_view(), name="comment_list"),
    path("<int:pk>/comments/", CommentCreateView.as_view(), name="comment_create"),
    path(
        "comments/<int:comment_pk>/", CommentDetailView.as_view(), name="comment_detail"
    ),
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
    path("<int:pk>/like/", LikeView.as_view(), name="click_like"),
    path(
        "<int:location_id>/posts/",
        PostsByLocationView.as_view(),
        name="posts_by_location",
    ),
    path("user/<int:user_id>/", GetUserPost, name="get_user_post"),  # 엔드포인트 추가
]
