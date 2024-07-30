import boto3
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
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
            # 유효한 데이터를 기반으로 새로운 게시물 생성 및 저장
            post = serializer.save()
            # 임시 이미지 ID 목록을 문자열에서 정수 리스트로 변환
            temp_image_ids_str = request.data.get("temp_image_ids", "")
            temp_image_ids = (
                list(map(int, temp_image_ids_str.split(",")))
                if temp_image_ids_str
                else []
            )
            for image_id in temp_image_ids:
                try:
                    # 해당 ID를 가진 이미지 객체 가져옴
                    image = Image.objects.get(id=image_id)
                    # 이미지의 board 필드를 새로운 게시물로 설정하고 저장
                    image.board = post
                    image.save()
                    # 게시물의 이미지 목록에 추가
                    post.images.add(image)
                except Image.DoesNotExist:
                    pass
             # 최종적으로 업데이트된 PostSerializer를 사용하여 데이터를 응답으로 반환
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

#해당 유저가 작성한 게시물 목록 반환 api
@api_view(["GET"])
def GetUserPost(request, user_id):
    if request.method == "GET":
        # user_id에 해당하는 사용자의 게시물들을 필터링
        user_posts = Post.objects.filter(user_id=user_id)
        serializer = PostListSerializer(user_posts, many=True)
        return Response(serializer.data)

#게시물 상세 조회/삭제/수정 api
class PostDetailView(APIView):
    @swagger_auto_schema(
        operation_description="게시물 상세 조회",
        responses={
            200: DetailPostSerializer,
            404: "Not Found",
        },
    )
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        images = Image.objects.filter(board=pk)

        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data

        # 로그인/비로그인 유저 세션키 가져오기
        if request.user.is_authenticated:
            session_key = f"user_{request.user.id}_post_{pk}"
        else:
            ip_address = request.META.get("REMOTE_ADDR")
            session_key = f"anonymous_{ip_address}_post_{pk}"

        # 세션 키를 확인하여 조회수를 한 번만 증가시킵니다.
        if not request.session.get(session_key, False):
            Post.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
            request.session[session_key] = True

        response_data = {
            "post": post_data,
            "images": image_data,
        }

        return JsonResponse(response_data)

    @swagger_auto_schema(responses={204: "No Content"})
    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data)

        if serializer.is_valid():
            # 게시물을 저장
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

            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#전체 댓글 목록 조회 api
class CommentListView(APIView):
    @swagger_auto_schema(
        operation_description="전체 댓글 목록 조회",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request):
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

#댓글 작성 api
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

#댓글 조회/수정/삭제 api
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

#이미지 s3에 올리고 url 받아 로드api
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
         # request.FILES에서 "images"라는 이름의 파일 리스트를 가져옴
        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"error": "No images provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        image_instances = []
        temp_image_ids = []
        for image in images:
            # 이미지 객체를 생성하고 데이터베이스에 저장
            image_instance = Image(image=image)
            image_instance.save()
            image_instances.append(image_instance)
            temp_image_ids.append(image_instance.id)

         # 이미지들을 시리얼라이즈하여 응답으로 반환
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
            # 사용자가 이미 해당 게시물에 좋아요를 눌렀는지 확인
            like = Like.objects.get(user=user, post=post)
            # 좋아요를 취소하고 해당 객체를 삭제
            like.delete()
            return Response(
                {"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT
            )
        except Like.DoesNotExist:
            Like.objects.create(user=user, post=post)
            return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)


class PostsByLocationView(generics.ListAPIView):
    serializer_class = PostListSerializer

    def get_queryset(self):
        location_id = self.kwargs["location_id"]
        return Post.objects.filter(location__location_id=location_id)[:8]
