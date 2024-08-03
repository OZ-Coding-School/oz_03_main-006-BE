from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# 커스텀 페이지네이션 클래스 정의
class CustomPagination(PageNumberPagination):
    # 페이지당 표시할 항목 수 (여기서는 8개의 게시물)
    page_size = 8
    # 최대 페이지 수를 80개로 제한 (즉, 최대 640개의 게시물까지 표시 가능)
    max_page_size = 8 * 80

    # 커스텀된 페이징 응답을 반환하는 메서드
    def get_paginated_response(self, data):
        # 총 페이지 수를 계산하되, 최대 80페이지로 제한
        total_pages = min(self.page.paginator.num_pages, 80)

        # 페이징 정보와 함께 응답 데이터를 반환
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),  # 다음 페이지의 링크
                    "previous": self.get_previous_link(),  # 이전 페이지의 링크
                },
                "count": self.page.paginator.count,  # 전체 아이템 수
                "total_pages": total_pages,  # 제한된 총 페이지 수
                "page_size": self.page_size,  # 한 페이지당 아이템 수
                "results": data,  # 현재 페이지에 표시할 데이터
            }
        )
