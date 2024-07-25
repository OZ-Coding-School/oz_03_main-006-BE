import boto3
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Image, Like, Post
from .serializers import (
    CommentSerializer,
    DetailPostSerializer,
    ImageSerializer,
    PostListSerializer,
    PostSerializer,
)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)


# 게시물 작성(post), 전체 게시물 리스트 조회(get)
@api_view(["GET", "POST"])
def posts(request):
    if request.method == "GET":
        posts = get_list_or_404(Post)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
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
                    image = Image.objects.get(id=image_id)
                    image.board = post
                    image.save()
                    post.images.add(image)
                except Image.DoesNotExist:
                    pass
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    @swagger_auto_schema(
        operation_description="게시물 상세 조회",
        responses={
            200: DetailPostSerializer,
            404: "Not Found",
        },
    )
    def get(self, request, pk):
        # pk 값을 사용하여 특정 게시물을 가져옵니다.
        post = get_object_or_404(Post, pk=pk)

        # 게시물에 연결된 이미지를 가져옵니다.
        images = Image.objects.filter(board=pk)

        # 게시물 데이터를 직렬화합니다.
        post_data = DetailPostSerializer(post).data

        # 이미지를 직렬화합니다.
        image_data = ImageSerializer(images, many=True).data

        # 세션 키를 사용하여 조회수를 증가시킵니다.
        if request.user.is_authenticated:
            session_key = f"user_{request.user.id}_post_{pk}"
        else:
            ip_address = request.META.get("REMOTE_ADDR")
            session_key = f"anonymous_{ip_address}_post_{pk}"

        # 세션 키를 확인하여 조회수를 한 번만 증가시킵니다.
        if not request.session.get(session_key, False):
            Post.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
            request.session[session_key] = True

        # 응답 데이터를 구성합니다.
        response_data = {
            "post": post_data,
            "images": image_data,
        }

        # JSON 형식으로 응답합니다.
        return JsonResponse(response_data)

    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, pk):
        # pk 값을 사용하여 특정 게시물을 가져옵니다.
        post = get_object_or_404(Post, pk=pk)

        # 게시물을 삭제합니다.
        post.delete()

        # 204 No Content 상태로 응답합니다.
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def put(self, request, pk):
        # pk 값을 사용하여 특정 게시물을 가져옵니다.
        post = get_object_or_404(Post, pk=pk)

        # 요청 데이터를 사용하여 게시물을 직렬화합니다.
        serializer = PostSerializer(post, data=request.data)

        # 직렬화된 데이터가 유효한 경우
        if serializer.is_valid():
            # 게시물을 저장합니다.
            serializer.save()

            # 임시 이미지 ID를 가져와 처리합니다.
            temp_image_ids_str = request.data.get("temp_image_ids", "")
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )
            for image_id in temp_image_ids:
                try:
                    # 이미지를 가져와 게시물에 연결합니다.
                    image = Image.objects.get(id=image_id)
                    image.board = post
                    image.save()
                    post.images.add(image)
                except Image.DoesNotExist:
                    pass

            # 업데이트된 게시물을 직렬화합니다.
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        # 직렬화된 데이터가 유효하지 않은 경우 오류 응답을 반환합니다.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListView(APIView):
    @swagger_auto_schema(
        operation_description="전체 댓글 목록 조회",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request):
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


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


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={201: "좋아요", 204: "좋아요 취소", 404: "Not Found"}
    )
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user
        try:
            like = Like.objects.get(user=user, post=post)
            like.delete()
            return Response(
                {"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT
            )
        except Like.DoesNotExist:
            Like.objects.create(user=user, post=post)
            return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)
