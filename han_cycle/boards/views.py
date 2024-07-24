import boto3
from boards.serializers import (
    CommentSerializer,
    DetailPostSerializer,
    ImageSerializer,
    PostListSerializer,
    PostSerializer,
)
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Comment, Image, Post

# AWS S3 클라이언트 설정
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)


# 게시물 작성(post), 전체 게시물 리스트 조회(get)
@swagger_auto_schema(method="get", responses={200: PostListSerializer(many=True)})
@swagger_auto_schema(
    method="post",
    request_body=PostSerializer,
    responses={201: PostSerializer, 400: "Bad Request"},
)
@api_view(["GET", "POST"])
def posts(request):
    if request.method == "GET":
        posts = get_list_or_404(Post)
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # 게시물 생성 및 저장
            post = serializer.save()

            # 임시 이미지 ID들을 받아옴
            temp_image_ids_str = request.data.get(
                "temp_image_ids", ""
            )  # 기본값으로 빈 문자열 설정
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )

            # 임시 이미지 ID들로 실제 이미지 객체들을 찾아서 연결
            for image_id in temp_image_ids:
                try:
                    image = Image.objects.get(id=image_id)
                    image.board = post  # 이미지에 게시물을 연결
                    image.save()  # 변경사항 저장
                    post.images.add(image)  # 게시물에 이미지 추가
                except Image.DoesNotExist:
                    pass

            # 수정된 PostSerializer를 사용하여 게시물 정보와 이미지 정보를 포함한 응답을 반환
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 세부 게시물 조회(get), 게시물 삭제(delete), 수정(put)
@swagger_auto_schema(method="get", responses={200: DetailPostSerializer})
@swagger_auto_schema(method="delete", responses={204: "No Content", 404: "Not Found"})
@swagger_auto_schema(
    method="put",
    request_body=PostSerializer,
    responses={200: PostSerializer, 400: "Bad Request"},
)
@api_view(["GET", "DELETE", "PUT"])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    images = Image.objects.filter(board=pk)

    if request.method == "GET":
        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data

        # 세션 키 로그인 사용자는 로그인 아이디, 비로그인 사용자는 ip로 저장
        if request.user.is_authenticated:
            session_key = f"user_{request.user.id}_post_viewed_{pk}"
        else:
            ip_address = request.META.get("REMOTE_ADDR")
            session_key = f"anonymous_{ip_address}_post_viewed_{pk}"

        # 조회기록 확인 후 +1
        if not request.session.get(session_key, False):
            Post.objects.filter(pk=pk).update(view_count=Post.view_count + 1)
            request.session[session_key] = True

        response_data = {
            "post": post_data,
            "images": image_data,
        }
        return JsonResponse(response_data)

    elif request.method == "DELETE":
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == "PUT":
        serializer = PostSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()

            # 임시 이미지 ID들을 받아옴
            temp_image_ids_str = request.data.get(
                "temp_image_ids", ""
            )  # 기본값으로 빈 문자열 설정
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )

            # 임시 이미지 ID들로 실제 이미지 객체들을 찾아서 연결
            for image_id in temp_image_ids:
                try:
                    image = Image.objects.get(id=image_id)
                    image.board = post  # 이미지에 게시물을 연결
                    image.save()  # 변경사항 저장
                    post.images.add(image)  # 게시물에 이미지 추가
                except Image.DoesNotExist:
                    pass

            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 전체 댓글 목록 조회
@swagger_auto_schema(method="get", responses={200: CommentSerializer(many=True)})
@api_view(["GET"])
def comment_list(request):
    if request.method == "GET":
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# 댓글 작성
@swagger_auto_schema(
    method="post",
    request_body=CommentSerializer,
    responses={201: CommentSerializer, 400: "Bad Request"},
)
@api_view(["POST"])
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# 댓글 조회(get), 삭제(delete), 수정(put)
@swagger_auto_schema(method="get", responses={200: CommentSerializer})
@swagger_auto_schema(method="delete", responses={204: "No Content", 404: "Not Found"})
@swagger_auto_schema(
    method="put",
    request_body=CommentSerializer,
    responses={200: CommentSerializer, 400: "Bad Request"},
)
@api_view(["GET", "DELETE", "PUT"])
def comment_detail(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.method == "GET":
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == "DELETE":
        comment.delete()
        data = {"delete": f"댓글 {comment_pk}번이 삭제 되었습니다."}
        return Response(data, status=status.HTTP_204_NO_CONTENT)

    elif request.method == "PUT":
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


# 게시물 본문 작성시 이미지 s3에 올리고 url반환
@swagger_auto_schema(
    method="post",
    manual_parameters=[
        openapi.Parameter(
            "images",
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description="Images to upload",
            required=True,
        )
    ],
    responses={201: ImageSerializer(many=True), 400: "Bad Request"},
)
@api_view(["POST"])
def upload_image(request):
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
