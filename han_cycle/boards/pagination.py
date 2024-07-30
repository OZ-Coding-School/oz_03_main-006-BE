from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 8  # 한페이지에 8개의 게시물
    max_page_size = 8 * 80  # 총 페이지 수를 80개로 제한 (한 페이지에 8개의 게시물 기준)

    def get_paginated_response(self, data):
        # 총 페이지 수가 80개를 초과하지 않도록 제한
        total_pages = min(self.page.paginator.num_pages, 80)

        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "total_pages": total_pages,  # 총 페이지 수
                "page_size": self.page_size,
                "results": data,
            }
        )
