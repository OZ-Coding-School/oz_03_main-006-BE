from django.urls import path

from .views import (
    CommentCreateView,
    CommentDetailView,
    CommentListView,
    GetUserPost,
    LikeView,
    PostDetailView,
    PostsByLocationLatestView,
    PostsByLocationPopularView,
    UploadImageView,
    posts,
    AllPostsByLocationLatestView,  
    AllPostsByLocationPopularView,
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
    path("user/<int:user_id>/", GetUserPost, name="get_user_post"),
    path(
        "<int:location_id>/latest/",
        PostsByLocationLatestView.as_view(),
        name="posts_by_location_latest",
    ),
    path(
        "<int:location_id>/popular/",
        PostsByLocationPopularView.as_view(),
        name="posts_by_location_popular",
    ),
    path(
        "<int:location_id>/all/latest/",
        AllPostsByLocationLatestView.as_view(),
        name="all_posts_by_location_latest",
    ),
    path(
        "<int:location_id>/all/popular/",
        AllPostsByLocationPopularView.as_view(),
        name="all_posts_by_location_popular",
    ),
]
