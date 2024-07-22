from .models import Post, Image, Comment
from boards.serializers import PostListSerializer, PostSerializer, CommentSerializer, ImageSerializer, DetailPostSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

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
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # 게시물 생성 및 저장
            post = serializer.save()
            #print(f"게시물 생성 완료: {post.title}, ID: {post.id}")  # 로그 추가
            
            # 임시 이미지 ID들을 받아옴
            temp_image_ids_str = request.data.get('temp_image_ids', '')  # 기본값으로 빈 문자열 설정
            temp_image_ids = list(map(int, temp_image_ids_str.split(','))) if temp_image_ids_str else []
            print(f"임시 이미지 ID들: {temp_image_ids}")  # 로그 추가
            
            # 임시 이미지 ID들로 실제 이미지 객체들을 찾아서 연결
            for image_id in temp_image_ids:
                try:
                    image = Image.objects.get(id=image_id)
                    image.board = post  # 이미지에 게시물을 연결
                    image.save()  # 변경사항 저장
                    post.images.add(image)  # 게시물에 이미지 추가
                    print(f"이미지 연결 완료: 이미지 ID {image_id} -> 게시물 ID {post.id}")  # 로그 추가
                except Image.DoesNotExist:
                    print(f"이미지를 찾을 수 없습니다: 이미지 ID {image_id}")  # 로그 추가
                    pass
            
            # 수정된 PostSerializer를 사용하여 게시물 정보와 이미지 정보를 포함한 응답을 반환
            updated_serializer = PostSerializer(post)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
        
        # serializer.is_valid()가 False인 경우에 대한 처리
        print(f"유효하지 않은 데이터: {serializer.errors}")  # 로그 추가
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # request.method가 'POST'가 아닌 경우에 대한 처리
    print("POST 메서드가 아닙니다.")  # 로그 추가
    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#세부 게시물 조회(get), 게시물 삭제(delete), 수정(put)
@api_view(['GET', 'DELETE', 'PUT'])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    images = Image.objects.filter(board=pk)
   

    if request.method == 'GET':
        post_data = DetailPostSerializer(post).data
        image_data = ImageSerializer(images, many=True).data
        response_data = {
        'post': post_data,
        'images': image_data,
        }
        return JsonResponse(response_data)
    
    elif request.method == 'DELETE':
        user_id = request.data.get('user_id') 
        try:
            user_id = int(user_id)  # user_id를 정수로 변환
        except ValueError:
            # user_id가 정수로 변환할 수 없는 경우 처리
            return Response({'error': '유효하지 않은 user_id입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        if post.user_id.id == user_id:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else :
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        try_id = request.data.get('try_id') 
        try:
            user_id = int(try_id)  # user_id를 정수로 변환
        except ValueError:
            # user_id가 정수로 변환할 수 없는 경우 처리
            return Response({'error': '유효하지 않은 user_id입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        if post.user_id.id == user_id:
            try:
                serializer = PostSerializer(post, data=request.data)
        
                if serializer.is_valid():
                    serializer.save()
            
                    # 임시 이미지 ID들을 받아옴
                    temp_image_ids_str = request.data.get('temp_image_ids', '')  # 기본값으로 빈 문자열 설정
                    temp_image_ids = list(map(int, temp_image_ids_str.split(','))) if temp_image_ids_str else []
                    print(f"임시 이미지 ID들: {temp_image_ids}")  # 로그 추가
            
                    # 임시 이미지 ID들로 실제 이미지 객체들을 찾아서 연결
                    for image_id in temp_image_ids:
                        try:
                            image = Image.objects.get(id=image_id)
                            image.board = post  # 이미지에 게시물을 연결
                            image.save()  # 변경사항 저장
                            post.images.add(image)  # 게시물에 이미지 추가
                            print(f"이미지 연결 완료: 이미지 ID {image_id} -> 게시물 ID {post.id}")  # 로그 추가
                        except Image.DoesNotExist:
                            print(f"이미지를 찾을 수 없습니다: 이미지 ID {image_id}")  # 로그 추가
                            pass
            
                    updated_serializer = PostSerializer(post)
                    return Response(updated_serializer.data, status=status.HTTP_200_OK)
        
                print(f"유효하지 않은 데이터: {serializer.errors}")  # 로그 추가
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
            except Post.DoesNotExist:
                return Response({'error': '해당 ID의 게시물을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        else :
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        

#전체 댓글 목록 조회
@api_view(['GET'])
def comment_list(request):
    if request.method == 'GET':
        # comments = Comment.objects.all()
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
        data= {
            'delete' :f'댓글 {comment_pk}번이 삭제 되었습니다.'
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)
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
