from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from elasticsearch_dsl import Search
from .search_indexes import ArticleIndex

class SearchView(APIView):
    @swagger_auto_schema(
        operation_description="Search articles by query",
        manual_parameters=[
            openapi.Parameter(
                "q", openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING
            ),
        ],
        responses={200: "Success", 400: "Bad Request"},
    )
    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        s = Search(using="default", index="articles").query(
            "multi_match", query=query, fields=["title", "content"]
        )
        response = s.execute()
        results = [hit.to_dict() for hit in response]
        return Response({"results": results, "query": query}, status=status.HTTP_200_OK)