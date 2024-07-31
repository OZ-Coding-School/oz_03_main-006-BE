import datetime
import random
import string

import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserProfileForm
from .models import User
from .serializers import UserSerializer


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer, responses={201: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        """
        사용자 등록 API
        - 데이터 유효성 검사 후 사용자 생성
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(
            raise_exception=True
        )  # Raise exception if the data is invalid
        serializer.save()
        return Response(serializer.data, status=201)


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User nickname"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User password"
                ),
            },
            required=["nickname", "password"],
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "id": 1,
                        "nickname": "example_user",
                        "profile_image": "example_image_url",
                        "email": "user@example.com",
                        "username": "example_username",
                        # No JWT here
                    }
                },
            ),
            400: "Bad Request",
            401: "Authentication Failed",
        },
    )
    def post(self, request):
        """
        로그인 API
        - 닉네임과 비밀번호로 사용자 인증 후 JWT 토큰 발급
        """
        nickname = request.data.get("nickname")
        password = request.data.get("password")

        user = User.objects.filter(nickname=nickname).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Set the JWT token in an HTTP-only cookie
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)

        # Serialize the user data without including the JWT token
        user_data = UserSerializer(user).data
        response.data = user_data

        return response


class UserView(APIView):
    @swagger_auto_schema(responses={200: UserSerializer, 401: "Unauthenticated"})
    def get(self, request):
        """
        사용자 정보 조회 API
        - JWT 토큰을 통해 인증된 사용자 정보 반환
        """
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload["id"]).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    @swagger_auto_schema(responses={200: "Successfully logged out"})
    def post(self, request):
        """
        로그아웃 API
        - JWT 토큰 삭제
        """
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "Successfully logged out"}
        return response


def googleredirect(request):
    state = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    request.session["oauth_state"] = state
    return redirect(
        f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20email%20profile&state={state}"
    )


class EditProfileView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer, responses={200: UserSerializer, 400: "Bad Request"}
    )
    @method_decorator(login_required)
    def post(self, request):
        """
        프로필 수정 API
        - 로그인된 사용자가 자신의 프로필 정보를 수정
        """
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
