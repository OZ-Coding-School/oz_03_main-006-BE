from django.http import JsonResponse

def health_check(request):
    """
    로드밸런서 health check를 위한 뷰. 성공 시 200 OK 응답.
    """
    return JsonResponse({"status": "ok"}, status=200)