import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import (
    User,
)  # User 모델을 가져옵니다. (users 앱에 위치하고 있다고 가정)
from users.serializers import UserUpdateSerializer  # UserUpdateSerializer를 가져옵니다.


class UpdateProfileView(APIView):
    """
    사용자가 자신의 프로필 정보를 업데이트할 수 있는 API 뷰입니다.
    JWT 토큰을 사용하여 사용자를 인증하고, 인증된 사용자의 프로필을 업데이트합니다.
    """

    def post(self, request):
        # 사용자의 JWT 토큰을 쿠키에서 가져옵니다.
        token = request.COOKIES.get("jwt")

        # 토큰이 없는 경우 인증 실패 예외를 발생시킵니다.
        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            # JWT 토큰을 디코드하여 사용자 정보를 가져옵니다.
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            # 토큰이 만료된 경우 인증 실패 예외를 발생시킵니다.
            raise AuthenticationFailed("Unauthenticated!")

        # 디코드된 토큰에서 사용자 ID를 사용하여 사용자 객체를 가져옵니다.
        user = User.objects.filter(id=payload["id"]).first()

        # 요청된 데이터로 사용자 프로필을 업데이트하기 위해 시리얼라이저를 사용합니다.
        # partial=True는 부분 업데이트를 허용합니다 (모든 필드를 제공할 필요 없음).
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        # 유효성 검사를 수행하고, 오류가 있는 경우 예외를 발생시킵니다.
        serializer.is_valid(raise_exception=True)
        # 사용자 정보를 업데이트하고 저장합니다.
        serializer.save()

        # 업데이트된 사용자 데이터를 응답으로 반환합니다.
        return Response(serializer.data)
