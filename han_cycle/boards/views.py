from .models import Post, Image, Comment, Like
from users.models import User
from boards.serializers import PostListSerializer, PostSerializer, CommentSerializer, ImageSerializer, DetailPostSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view,  permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, get_list_or_404
import boto3
from django.conf import settings
from django.http import JsonResponse
s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          region_name=settings.AWS_S3_REGION_NAME)


#게시물 작성(post), 전체 게시물 리스트 조회(get)   
@api_view(['GET', 'POST'])
def posts(request):
    if request.method=='GET':
        posts=get_list_or_404(Post)
        serializer=PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        """
        # 현재 인증된 사용자
        user = request.user
    
        # 게시물 생성을 위한 Serializer 인스턴스 생성
        serializer_data = request.data.copy()  # 데이터 복사
        serializer_data['user_id'] = user.id  # Serializer 데이터에 user_id 추가
        # serializer_data에 request.data를 병합하여 사용
        serializer_data.update(request_data)
        serializer = PostSerializer(data=serializer_data)
        """
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # 게시물 생성 및 저장
            post = serializer.save()
            
            # 임시 이미지 ID들을 받아옴
            temp_image_ids_str = request.data.get('temp_image_ids', '')  # 기본값으로 빈 문자열 설정
            temp_image_ids = list(map(int, temp_image_ids_str.split(','))) if temp_image_ids_str else []
            
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
        
        # serializer.is_valid()가 False인 경우에 대한 처리
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#세부 게시물 조회(get), 게시물 삭제(delete), 수정(put)
@api_view(['GET', 'DELETE', 'PUT'])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    images = Image.objects.filter(board=pk)
   
    if request.method == 'GET':
        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data
        
        # 세션 키 로그인 사용자는 로그인 아이디, 비로그인 사용자는 ip로 저장
        if request.user.is_authenticated:
            session_key = f'user_{request.user.id}_post_{pk}'
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            session_key = f'anonymous_{ip_address}_post_{pk}'

        # 조회기록 확인 후 +1
        if not request.session.get(session_key, False):
            Post.objects.filter(pk=pk).update(view_count=Post.view_count + 1)
            request.session[session_key] = True
        
        

        response_data = {
        'post': post_data,
        'images': image_data,
        }
        return JsonResponse(response_data)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        """
        # 현재 인증된 사용자
        user = request.user
    
        # 게시물 생성을 위한 Serializer 인스턴스 생성
        serializer_data = request.data.copy()  # 데이터 복사
        serializer_data['user_id'] = user.id  # Serializer 데이터에 user_id 추가
        # serializer_data에 request.data를 병합하여 사용
        serializer_data.update(request_data)
        serializer = PostSerializer(data=serializer_data)
        """
        try:
            serializer = PostSerializer(post, data=request.data)
        
            if serializer.is_valid():
                # 기존 데이터 업데이트
                serializer.save()
            
                # 임시 이미지 ID들을 받아옴
                temp_image_ids_str = request.data.get('temp_image_ids', '')  # 기본값으로 빈 문자열 설정
                temp_image_ids = list(map(int, temp_image_ids_str.split(','))) if temp_image_ids_str else []
                
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
    
        except Post.DoesNotExist:
            return Response({'error': '해당 ID의 게시물을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        

#전체 댓글 목록 조회
@api_view(['GET'])
def comment_list(request):
    if request.method == 'GET':
        comments = get_list_or_404(Comment)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

#댓글작성    
@api_view(['POST'])
def comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
       

#댓글 조회(get), 삭제(delete), 수정(put)   
@api_view(['GET', 'DELETE', 'PUT'])
def comment_detail(request, comment_pk) :
    comment = get_object_or_404(Comment, pk = comment_pk)
    if request.method == 'GET' :
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    elif request.method == "DELETE" :
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == "PUT" :
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid(raise_exception=True) :
            serializer.save()
            return Response(serializer.data)

#게시물 본문 작성시 이미지 s3에 올리고 url반환
@api_view(['POST'])
def upload_image(request):
    images = request.FILES.getlist('images')
    
    if not images:
        return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    image_instances = []
    temp_image_ids = []  # 임시 이미지 ID를 저장할 리스트
    
    for image in images:
        image_instance = Image(image=image)
        image_instance.save()  # 이미지를 먼저 저장하고
        image_instances.append(image_instance)
        temp_image_ids.append(image_instance.id)  # 임시 이미지 ID를 리스트에 추가
    
    serializer = ImageSerializer(image_instances, many=True)
    return Response({'temp_image_ids': temp_image_ids, 'images': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated]) # 로그인한 사용자만 api에 접근가능
def click_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    #postman 테스트용 코드
    #user_id = request.data.get('user_id', None)
    #user = User.objects.get(id=user_id)
    try:
        like = Like.objects.get(user=user, post=post)
        # 이미 좋아요가 있는 경우 삭제
        like.delete()
        return Response({"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        # 좋아요 추가
        Like.objects.create(user=user, post=post)
        return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)