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
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import Comment, Image, Post

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)


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


@swagger_auto_schema(method="get", responses={200: DetailPostSerializer})
@swagger_auto_schema(
    method="delete",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID")
        },
    ),
    responses={204: "No Content", 400: "Bad Request"},
)
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
        response_data = {
            "post": post_data,
            "images": image_data,
        }
        return JsonResponse(response_data)

    elif request.method == "DELETE":
        user_id = request.data.get("user_id")
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {"error": "유효하지 않은 user_id입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if post.user_id.id == user_id:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

    elif request.method == "PUT":
        try_id = request.data.get("try_id")
        try:
            user_id = int(try_id)
        except ValueError:
            return Response(
                {"error": "유효하지 않은 user_id입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if post.user_id.id == user_id:
            serializer = PostSerializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
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
                return Response(updated_serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )


@swagger_auto_schema(method="get", responses={200: CommentSerializer(many=True)})
@api_view(["GET"])
def comment_list(request):
    if request.method == "GET":
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


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
@parser_classes([MultiPartParser])
def upload_image(request):
    images = request.FILES.getlist("images")

    if not images:
        return Response(
            {"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    image_instances = []
    temp_image_ids = []  # 임시 이미지 ID를 저장할 리스트

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
