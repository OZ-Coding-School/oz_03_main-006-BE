from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from elasticsearch_dsl import Search
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .search_index import LocationIndex, PostIndex, UserIndex


class SearchView(APIView):
    # Swagger 자동 스키마 생성을 위한 데코레이터
    @swagger_auto_schema(
        operation_description="검색어를 입력하세요.",  # API 설명
        manual_parameters=[  # 쿼리 매개변수 정의
            openapi.Parameter(
                "q",  # 매개변수 이름
                openapi.IN_QUERY,  # 매개변수 위치 (쿼리 파라미터)
                description="검색어",  # 설명
                type=openapi.TYPE_STRING,  # 데이터 타입
            ),
        ],
        responses={200: "Success", 400: "Bad Request"},  # 가능한 응답 상태 코드
    )
    def get(self, request):
        query = request.GET.get("q", "")  # 쿼리 파라미터 'q'의 값을 가져옴
        if not query:  # 'q' 파라미터가 없는 경우
            return Response(
                {"error": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request 응답 반환
            )

        # 'posts' 인덱스에서 제목과 내용 필드를 검색
        post_search = Search(using="default", index="posts").query(
            "multi_match", query=query, fields=["title", "content"]
        )
        # 'users' 인덱스에서 닉네임과 이메일 필드를 검색
        user_search = Search(using="default", index="users").query(
            "multi_match", query=query, fields=["nickname", "email"]
        )
        # 'locations' 인덱스에서 도시, 설명, 하이라이트 필드를 검색
        location_search = Search(using="default", index="locations").query(
            "multi_match", query=query, fields=["city", "description", "highlights"]
        )

        # 각각의 검색 쿼리 실행
        post_response = post_search.execute()
        user_response = user_search.execute()
        location_response = location_search.execute()

        # 검색 결과를 리스트로 변환
        post_results = [
            {
                "title": hit.title,
                "content": hit.content,
                "created_at": hit.created_at,
                "id": hit.meta.id,
            }
            for hit in post_response
        ]
        user_results = [
            {"nickname": hit.nickname, "email": hit.email, "id": hit.meta.id}
            for hit in user_response
        ]
        location_results = [
            {
                "city": hit.city,
                "description": hit.description,
                "highlights": hit.highlights,
                "id": hit.meta.id,
            }
            for hit in location_response
        ]

        # 결과를 딕셔너리로 정리
        results = {
            "posts": post_results,
            "users": user_results,
            "locations": location_results,
            "query": query,
        }

        # 최종 응답 반환
        return Response({"results": results}, status=status.HTTP_200_OK)
