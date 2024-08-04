import boto3
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view

# from rest_framework.decorators import permissions_classes
from rest_framework.pagination import PageNumberPagination

# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Image, Like, Post, User
from .pagination import CustomPagination
from .serializers import (
    CommentSerializer,
    DetailPostSerializer,
    ImageSerializer,
    PostListSerializer,
    PostSerializer,
)


# 게시물 작성(post), 전체 게시물 리스트 조회(get)
@csrf_exempt  # 함수형 뷰에서 CSRF 비활성화
@api_view(["GET", "POST"])
def posts(request):
    if request.method == "GET":
        # 모든 게시물을 조회하여 리스트를 반환
        posts = get_list_or_404(Post)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        # 게시물 생성 요청을 처리
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            temp_image_ids_str = request.data.get("temp_image_ids", "")
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )
            for image_id in temp_image_ids:
                try:
                    # 이미지의 board를 post_id로 연결
                    image = Image.objects.get(id=image_id)
                    image.board = post
                    image.save()
                    post.images.add(image)
                except Image.DoesNotExist:
                    pass
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt  # 함수형 뷰에서 CSRF 비활성화
@swagger_auto_schema(
    method="get",
    operation_description="Retrieve a list of posts for a specific user.",
    responses={200: PostListSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter(
            "user_id",
            openapi.IN_PATH,
            description="ID of the user to retrieve posts for",
            type=openapi.TYPE_INTEGER,
        )
    ],
)

# 특정 사용자의 게시물 목록을 조회
@api_view(["GET"])
def GetUserPost(request, user_id):
    if request.method == "GET":
        user_posts = Post.objects.filter(user_id=user_id)
        serializer = PostListSerializer(user_posts, many=True)
        return Response(serializer.data)


# 게시물 상세 조회


@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class PostDetailView(APIView):
    @swagger_auto_schema(
        operation_description="게시물 상세 조회",
        responses={
            200: DetailPostSerializer,
            404: "Not Found",
        },
    )
    def get(self, request, pk):
        # pk 값을 사용하여 특정 게시물과 연결된 이미지르를 가져와 직렬화
        post = get_object_or_404(Post, pk=pk)
        images = Image.objects.filter(board=pk)
        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data

        session = request.COOKIES.get(f"post_{pk}")

        # 응답 데이터를 구성
        response_data = {
            f"post_{pk}": session,
            "post": post_data,
            "images": image_data,
        }

        # 쿠키를 확인하고 없는 경우 쿠키를 저장하고 조회수 증가
        if not session:
            Post.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
            response = JsonResponse(response_data)
            response.set_cookie(
                key=f"post_{pk}", value="True", httponly=True, samesite="Lax"
            )
            return response

        else:
            return JsonResponse(response_data)

    # 게시물 삭제
    @method_decorator(csrf_exempt)
    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    # 게시글 수정
    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # 임시 이미지 ID를 가져와 처리
            temp_image_ids_str = request.data.get("temp_image_ids", "")
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )
            for image_id in temp_image_ids:
                try:
                    # 이미지를 가져와 게시물에 연결
                    image = Image.objects.get(id=image_id)
                    image.board = post
                    image.save()
                    post.images.add(image)
                except Image.DoesNotExist:
                    pass

            # 업데이트된 게시물을 직렬화
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        # 직렬화된 데이터가 유효하지 않은 경우 오류 응답을 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 전체 댓글 목록 조회


@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class CommentListView(APIView):
    @swagger_auto_schema(
        operation_description="전체 댓글 목록 조회",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request):
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# 댓글작성


@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class CommentCreateView(APIView):
    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "Bad Request"},
    )
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 상세 댓글 조회, 수정, 삭제
@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class CommentDetailView(APIView):
    @swagger_auto_schema(
        operation_description="댓글 조회, 수정 및 삭제",
        responses={
            200: CommentSerializer,
            204: "No Content",
            400: "Bad Request",
            404: "Not Found",
        },
    )
    def get(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={200: CommentSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def put(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 게시글 본문 이미지 s3 버킷에 올리고 url로 반환


@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class UploadImageView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "images": openapi.Schema(
                    type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)
                )
            },
        ),
        responses={201: ImageSerializer(many=True), 400: "Bad Request"},
    )
    def post(self, request):
        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        image_instances = []
        temp_image_ids = []
        for image in images:
            image_instance = Image(image=image)
            image_instance.save()
            image_instances.append(image_instance)
            temp_image_ids.append(image_instance.id)
        serializer = ImageSerializer(image_instances, many=True)
        return Response(
            {"temp_image_ids": temp_image_ids, "images": serializer.data},
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")  # 클래스 기반 뷰 전체에서 CSRF 비활성화
class LikeView(APIView):
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the user"
                )
            },
            required=["user_id"],
        ),
        responses={
            201: "좋아요",
            204: "좋아요 취소",
            404: "Not Found",
            400: "Bad Request",
        },
    )
    # 좋아요
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        # user = request.user
        user_id = request.data.get("user_id")  # request.data에서 user_id 가져오기

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 좋아요가 있으면 좋아요를 취소하고 없으면 좋아요 생성
        try:
            like = Like.objects.get(user_id=user_id, post=post)
            like.delete()
            return Response(
                {"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT
            )
        except Like.DoesNotExist:
            Like.objects.create(user_id=user_id, post=post)
            return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="ID of the user",
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"result": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
            ),
            400: "Bad Request",
            404: "Not Found",
        },
    )
    # 좋아요 유무 조회
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user_id = request.query_params.get(
            "user_id"
        )  # 쿼리 파라미터에서 user_id 가져오기

        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            like = Like.objects.get(user_id=user_id, post=post)
            boolean_value = True
            data = {"result": boolean_value}
            return JsonResponse(data)
        except Like.DoesNotExist:
            boolean_value = False
            data = {"result": boolean_value}
            return JsonResponse(data)


@swagger_auto_schema(
    method="get",
    operation_description="Get posts liked by a specific user",
    responses={200: PostListSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter(
            "user_id",
            openapi.IN_PATH,
            description="ID of the user to retrieve liked posts for",
            type=openapi.TYPE_INTEGER,
        )
    ],
)

# 사용자별 좋아요 게시물 목록 조회
@api_view(["GET"])
def liked_posts(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # 해당 사용자가 좋아요한 모든 Like 객체를 가져오고, 해당 객체에서 Post_id를 가져와 게시물 목록 가져옴
    user_likes = Like.objects.filter(user=user)
    liked_post_ids = user_likes.values_list("post_id", flat=True)

    liked_posts = Post.objects.filter(id__in=liked_post_ids)

    serializer = PostListSerializer(liked_posts, many=True)
    return Response(serializer.data)


# 특정 위치의 최신 게시물 목록을 반환하는 뷰 클래스
class PostsByLocationLatestView(generics.ListAPIView):
    serializer_class = PostListSerializer  # 게시물 목록에 대한 직렬화 클래스
    pagination_class = CustomPagination  # 페이지네이션 설정

    @swagger_auto_schema(
        operation_description="특정 위치의 최신 게시물 목록을 가져옵니다.",
        responses={200: PostListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="위치의 ID",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        # GET 요청을 처리하여 최신 게시물 목록을 반환
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # 쿼리셋을 정의하여 특정 위치의 최신 게시물만 필터링
        location_id = self.kwargs["location_id"]
        return Post.objects.filter(location__location_id=location_id).order_by(
            "-created_at"
        )


# 특정 위치의 가장 인기 있는 게시물 목록을 반환하는 뷰 클래스
class PostsByLocationPopularView(generics.ListAPIView):
    serializer_class = PostListSerializer  # 게시물 목록에 대한 직렬화 클래스
    pagination_class = CustomPagination  # 페이지네이션 설정

    @swagger_auto_schema(
        operation_description="특정 위치의 가장 인기 있는 게시물 목록을 가져옵니다.",
        responses={200: PostListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="위치의 ID",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        # GET 요청을 처리하여 인기 있는 게시물 목록을 반환
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # 쿼리셋을 정의하여 특정 위치의 조회수가 가장 많은 게시물만 필터링
        location_id = self.kwargs["location_id"]
        return Post.objects.filter(location__location_id=location_id).order_by(
            "-view_count"
        )


# 전체 위치의 최신 게시물 목록을 반환하는 뷰 클래스
class AllPostsByLocationLatestView(generics.ListAPIView):
    serializer_class = PostListSerializer  # 게시물 목록에 대한 직렬화 클래스

    @swagger_auto_schema(
        operation_description="특정 위치의 모든 최신 게시물을 가져옵니다.",
        responses={200: PostListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="게시물을 가져올 위치의 ID",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        """
        특정 위치의 모든 최신 게시물을 가져옵니다.
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        # 쿼리셋을 정의하여 특정 위치의 모든 최신 게시물만 필터링
        location_id = self.kwargs["location_id"]
        return Post.objects.filter(location__location_id=location_id).order_by(
            "-created_at"
        )

    def list(self, request, *args, **kwargs):
        # 쿼리셋을 페이지네이션하고 직렬화하여 응답
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 전체 위치의 인기 있는 게시물 목록을 반환하는 뷰 클래스
class AllPostsByLocationPopularView(generics.ListAPIView):
    serializer_class = PostListSerializer  # 게시물 목록에 대한 직렬화 클래스

    @swagger_auto_schema(
        operation_description="특정 위치의 모든 인기 게시물을 가져옵니다.",
        responses={200: PostListSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "location_id",
                openapi.IN_PATH,
                description="게시물을 가져올 위치의 ID",
                type=openapi.TYPE_INTEGER,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        """
        특정 위치의 모든 인기 게시물을 가져옵니다.
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        # 쿼리셋을 정의하여 특정 위치의 모든 인기 있는 게시물만 필터링
        location_id = self.kwargs["location_id"]
        return Post.objects.filter(location__location_id=location_id).order_by(
            "-view_count"
        )

    def list(self, request, *args, **kwargs):
        # 쿼리셋을 페이지네이션하고 직렬화하여 응답
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
