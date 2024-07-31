import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RefreshToken, User
from .serializers import UserSerializer

User = get_user_model()


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
                        # Token not included in the response body
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
        - 닉네임과 비밀번호로 사용자 인증 후 JWT 토큰과 리프레시 토큰 발급
        """
        nickname = request.data.get("nickname")
        password = request.data.get("password")

        user = User.objects.filter(nickname=nickname).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        # Generate access token
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # Generate refresh token
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(
            days=30
        )  # Refresh token valid for 30 days
        refresh_token = RefreshToken.objects.create(user=user, expires_at=expires_at)

        # Set the JWT token in an HTTP-only cookie
        response = Response(
            {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image.url if user.profile_image else None,
                "email": user.email,
                "username": user.username,
                # Token not included in the response body
            }
        )
        response.set_cookie(key="jwt", value=access_token, httponly=True)
        response.set_cookie(
            key="refresh_token", value=str(refresh_token.token), httponly=True
        )

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


class NicknameView(APIView):
    @swagger_auto_schema(
        operation_description="닉네임 변경 API - JWT 토큰을 통해 인증된 사용자만 사용 가능. 요청 데이터에서 새로운 닉네임을 받아 사용자 닉네임을 업데이트합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 닉네임"
                ),
            },
            required=["nickname"],
        ),
        responses={
            200: openapi.Response(
                description="닉네임이 성공적으로 업데이트되었습니다.",
                examples={
                    "application/json": {"detail": "Nickname updated to new_nickname."}
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def put(self, request):
        """
        닉네임 변경 API
        - JWT 토큰을 통해 인증된 사용자만 사용 가능
        - 요청 데이터에서 새로운 닉네임을 받아 사용자 닉네임 업데이트
        """
        token = request.COOKIES.get("jwt")
        if not token:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        new_nickname = request.data.get("nickname")
        if not new_nickname:
            return Response(
                {"detail": "New nickname is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(nickname=new_nickname).exists():
            return Response(
                {"detail": "Nickname already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.nickname = new_nickname
        user.save()

        return Response(
            {f"Nickname updated to {user.nickname}."}, status=status.HTTP_200_OK
        )


class RefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="새로운 액세스 토큰을 발급하는 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="리프레시 토큰"
                ),
            },
            required=["refresh_token"],
        ),
        responses={
            200: openapi.Response(
                description="새로운 액세스 토큰 발급 성공",
                examples={"application/json": {"access_token": "new_access_token"}},
            ),
            401: "Unauthorized",
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        try:
            token = RefreshToken.objects.get(token=refresh_token, is_refresh_token=True)
        except RefreshToken.DoesNotExist:
            return Response({"detail": "Invalid refresh token."}, status=401)

        if not isinstance(token, RefreshToken):
            return Response({"detail": "Invalid token type."}, status=401)

        if token.is_expired():
            return Response({"detail": "Refresh token expired."}, status=401)

        user = token.user
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        new_access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({"access_token": new_access_token}, status=200)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="회원 탈퇴 API - JWT 토큰을 통해 인증된 사용자의 계정을 삭제합니다.",
        responses={
            204: "Account successfully deleted.",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def delete(self, request):
        """
        회원 탈퇴 API
        - JWT 토큰을 통해 인증된 사용자만 사용 가능
        - 인증된 사용자의 계정을 삭제함
        """
        token = request.COOKIES.get("jwt")
        if not token:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        response = Response(
            {"detail": "Account successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
        response.delete_cookie("jwt")

        return response


class PasswordResetRequestView(APIView):
    @swagger_auto_schema(
        operation_description="비밀번호 재설정 요청 API - 이메일 주소를 받아 비밀번호 재설정 링크를 이메일로 전송",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="사용자 이메일 주소"
                ),
            },
            required=["email"],
        ),
        responses={
            200: openapi.Response(
                description="비밀번호 재설정 링크가 이메일로 전송되었습니다.",
                examples={
                    "application/json": {
                        "reset_url": "https://example.com/reset-password?token=example_token"
                    }
                },
            ),
            404: "Not Found",
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            "id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        reset_url = request.build_absolute_uri(
            reverse("password-reset-confirm") + f"?token={token}"
        )

        return Response({"reset_url": reset_url}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(
        operation_description="비밀번호 재설정 API - 재설정 링크를 통해 받은 토큰과 새로운 비밀번호로 사용자 비밀번호를 업데이트",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="비밀번호 재설정 토큰"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 비밀번호"
                ),
            },
            required=["token", "new_password"],
        ),
        responses={
            200: "Password has been reset successfully.",
            400: "Bad Request",
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

        user_id = payload.get("id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
