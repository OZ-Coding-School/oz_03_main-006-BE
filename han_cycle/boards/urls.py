from django.urls import path

from .views import (
    AllPostsByLocationLatestView,
    AllPostsByLocationPopularView,
    CommentCreateView,
    CommentDetailView,
    CommentListView,
    GetUserPost,
    LikeView,
    PostDetailView,
    PostsByLocationLatestView,
    PostsByLocationPopularView,
    UploadImageView,
    liked_posts,
    posts,
)

# 게시판 관련 URL 패턴 정의
urlpatterns = [
    # 모든 게시물의 목록을 가져오거나 새 게시물을 작성하는 엔드포인트
    path("", posts, name="posts"),
    # 특정 게시물의 상세 정보를 가져오는 엔드포인트
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    # 모든 댓글 목록을 가져오는 엔드포인트
    path("comments/", CommentListView.as_view(), name="comment_list"),
    # 특정 게시물에 댓글을 추가하는 엔드포인트
    path("<int:pk>/comments/", CommentCreateView.as_view(), name="comment_create"),
    # 특정 댓글의 상세 정보 또는 삭제, 수정을 처리하는 엔드포인트
    path(
        "comments/<int:comment_pk>/", CommentDetailView.as_view(), name="comment_detail"
    ),
    # 이미지를 업로드하는 엔드포인트
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
    # 특정 게시물에 대해 '좋아요'를 추가하거나 취소하는 엔드포인트
    path("<int:pk>/like/", LikeView.as_view(), name="click_like"),
    # 특정 사용자가 작성한 게시물을 가져오는 엔드포인트
    path("user/<int:user_id>/", GetUserPost, name="get_user_post"),
    # 특정 사용자가 '좋아요'를 누른 게시물을 가져오는 엔드포인트
    path("user/<int:user_id>/liked_posts/", liked_posts, name="liked_posts"),
    # 특정 위치에서 최신 게시물 목록을 가져오는 엔드포인트
    path(
        "<int:location_id>/latest/",
        PostsByLocationLatestView.as_view(),
        name="posts_by_location_latest",
    ),
    # 특정 위치에서 인기 게시물 목록을 가져오는 엔드포인트
    path(
        "<int:location_id>/popular/",
        PostsByLocationPopularView.as_view(),
        name="posts_by_location_popular",
    ),
    # 특정 위치에서 모든 최신 게시물 목록을 가져오는 엔드포인트
    path(
        "<int:location_id>/all/latest/",
        AllPostsByLocationLatestView.as_view(),
        name="all_posts_by_location_latest",
    ),
    # 특정 위치에서 모든 인기 게시물 목록을 가져오는 엔드포인트
    path(
        "<int:location_id>/all/popular/",
        AllPostsByLocationPopularView.as_view(),
        name="all_posts_by_location_popular",
    ),
]
