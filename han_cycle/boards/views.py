from django.shortcuts import render,redirect
from .models import Post,Comment, Image
from django.contrib import messages
from .forms import PostForm

from boards.serializers import PostListSerializer,PostSerializer,CommentSerializer, DetailPostSerializer,ImageSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.shortcuts import get_object_or_404, get_list_or_404
import boto3
from django.conf import settings
import logging
from django.http import JsonResponse

s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)

@api_view(['GET', 'POST'])
def posts(request):
    if request.method=='GET':
        posts=get_list_or_404(Post)
        serializer=PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        

@api_view(['GET', 'DELETE', 'PUT'])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    images = Image.objects.filter(board=pk)
   

    if request.method == 'GET':
        #serializer = DetailPostSerializer(post)
        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data
        #return Response(serializer.data)
        response_data = {
        'post': post_data,
        'images': image_data,
        }
        return JsonResponse(response_data)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

@api_view(['GET'])
def comment_list(request):
    if request.method == 'GET':
        # comments = Comment.objects.all()
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
@api_view(['POST'])
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET', 'DELETE', 'PUT'])
def comment_detail(request, comment_pk) :
    comment = get_list_or_404(Comment, pk = comment_pk)
    if request.method == 'GET' :
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    elif request.method == "DELETE" :
        comment.delete()
        data= {
            'delete' :f'댓글 {comment_pk}번이 삭제 되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)
    elif request.method == "PUT" :
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid(raise_exception=True) :
            serializer.save()
            return Response(serializer.data)
        


logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_images(request, post_id):

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    images = request.FILES.getlist('images')
    if not images:
        return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

    image_instances = []
    for image in images:
        image_instance = Image(board=post, image=image)
        image_instances.append(image_instance)

    Image.objects.bulk_create(image_instances)

    serializer = ImageSerializer(image_instances, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
    

def board(request):
    # 모든 Post를 가져와 postlist에 저장합니다
    postlist = Post.objects.all()
    return render(request, 'boards/board.html', {'postlist':postlist})

# 세부 게시글 들어가기
def post(request, pk):
    # 게시글(Post) 중 pk(primary_key)를 이용해 하나의 게시글(post)를 검색
    post = Post.objects.get(pk=pk)
    # posting.html 페이지를 열 때, 찾아낸 게시글(post)을 post라는 이름으로 가져옴
    return render(request, 'boards/post.html', {'post':post})


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '게시물이 성공적으로 등록되었습니다.')
            return redirect('/posts')  # 게시물 리스트 페이지로 리디렉션 (URL 이름은 프로젝트에 맞게 변경)
        else:
            messages.error(request, '폼에 오류가 있습니다. 다시 시도해 주세요.')
    else:
        form = PostForm()
    
    return render(request, 'boards/new_post.html', {'form': form})