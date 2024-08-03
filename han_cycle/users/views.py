import datetime

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RefreshToken
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)

User = get_user_model()  # 현재 프로젝트에서 사용 중인 사용자 모델을 가져옵니다.


# 회원가입으로 사용자 생성
class RegisterView(APIView):
    """
    사용자가 회원가입을 통해 계정을 생성하는 뷰입니다.
    """

    @swagger_auto_schema(
        request_body=UserSerializer, responses={201: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        """
        사용자 등록 API
        - 주어진 데이터로 사용자를 생성합니다.
        """
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


# 로그인 (닉네임과 비밀번호로 사용자 인증)
class LoginView(APIView):
    """
    사용자가 로그인하여 JWT 토큰을 발급받는 뷰입니다.
    """

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
                description="로그인 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "nickname": "example_user",
                        "profile_image": "example_image_url",
                        "email": "user@example.com",
                        "username": "example_username",
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
        - 닉네임과 비밀번호를 통해 사용자를 인증한 후 JWT 토큰과 리프레시 토큰을 발급합니다.
        """
        nickname = request.data.get("nickname")
        password = request.data.get("password")

        user = User.objects.filter(nickname=nickname).first()

        if user is None:
            raise AuthenticationFailed("회원정보가 없습니다")

        if not user.check_password(password):
            raise AuthenticationFailed("패스워드가 틀렸습니다")

        # 엑세스 토큰 생성 (7일 동안 유효)
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # 리프레쉬 토큰 생성 (30일 동안 유효)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        refresh_token = RefreshToken.objects.create(user=user, expires_at=expires_at)

        # JWT 토큰을 HTTP-only 쿠키에 저장 (브라우저에서 접근 불가)
        response = Response(
            {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image.url if user.profile_image else None,
                "email": user.email,
                "username": user.username,
            }
        )
        response.set_cookie(
            key="jwt",
            value=access_token,
            httponly=True,
            expires=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token.token),
            httponly=True,
            expires=expires_at,
        )

        return response


# 사용자 정보 조회
class UserView(APIView):
    """
    현재 로그인한 사용자의 정보를 조회하는 뷰입니다.
    """

    @swagger_auto_schema(responses={200: UserSerializer, 401: "Unauthenticated"})
    def get(self, request):
        """
        사용자 정보 조회 API
        - JWT 토큰을 통해 인증된 사용자 정보를 반환합니다.
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


# 로그아웃
# JWT 및 리프레쉬 토큰 쿠키 삭제
class LogoutView(APIView):
    """
    사용자가 로그아웃할 때 JWT 및 리프레시 토큰을 삭제하는 뷰입니다.
    """

    @swagger_auto_schema(responses={200: "성공적으로 로그아웃이 되었습니다"})
    def post(self, request):
        """
        로그아웃 API
        - 사용자의 JWT 토큰과 리프레시 토큰을 삭제합니다.
        """
        response = Response()
        response.delete_cookie("jwt")
        response.delete_cookie("refresh_token")
        response.data = {"message": "성공적으로 로그아웃이 되었습니다"}
        return response


# 리프레쉬 토큰 (엑세스 토큰 재발급)
class RefreshTokenView(APIView):
    """
    리프레시 토큰을 사용하여 새로운 엑세스 토큰을 발급하는 뷰입니다.
    """

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
        """
        리프레시 토큰을 검증하여 새로운 액세스 토큰을 발급합니다.
        """
        refresh_token = request.data.get("refresh_token")
        try:
            token = RefreshToken.objects.get(token=refresh_token, is_refresh_token=True)
        except RefreshToken.DoesNotExist:
            return Response({"detail": "Invalid refresh token."}, status=401)

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


# 쿠키 인증 (비밀번호 재설정을 위한 토큰 인증)
class CookieAuthentication(BasePermission):
    """
    쿠키에 저장된 JWT 토큰을 통해 사용자를 인증하는 클래스입니다.
    """

    def has_permission(self, request, view):
        token = request.COOKIES.get("jwt")
        if not token:
            return False

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = User.objects.get(id=payload["id"])
            return True
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(_("Token has expired."))
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(_("Invalid token."))
        except User.DoesNotExist:
            raise AuthenticationFailed(_("User not found."))

        return False


# 계정 삭제 (JWT 쿠키 및 사용자 계정 삭제)
class DeleteAccountView(APIView):
    """
    사용자가 자신의 계정을 삭제할 수 있는 뷰입니다.
    """

    permission_classes = [CookieAuthentication]

    @swagger_auto_schema(
        operation_description="회원 탈퇴 API - JWT 토큰을 통해 인증된 사용자의 계정을 삭제합니다.",
        responses={
            204: "계정이 성공적으로 삭제되었습니다.",
            401: "인증되지 않았습니다.",
            404: "사용자를 찾을 수 없습니다.",
        },
    )
    def delete(self, request):
        """
        JWT 토큰을 통해 인증된 사용자의 계정을 삭제합니다.
        """
        token = request.COOKIES.get("jwt")
        if not token:
            return Response(
                {"detail": "인증 자격 증명이 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "토큰이 만료되었습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.delete()

        response = Response(
            {"detail": "계정이 성공적으로 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
        response.delete_cookie("jwt")

        return response


# 비밀번호 재설정 요청
class PasswordResetRequestView(APIView):
    """
    사용자가 비밀번호 재설정을 요청할 수 있는 뷰입니다.
    이메일을 통해 비밀번호 재설정 링크를 전송합니다.
    """

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

        # JWT 토큰을 생성하여 이메일로 전송할 URL에 포함시킵니다.
        payload = {
            "id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        reset_url = request.build_absolute_uri(
            reverse("password-reset-confirm") + f"?token={token}"
        )

        # 비밀번호 재설정 이메일을 전송합니다.
        subject = "Password Reset Request"
        message = f"Hello,\n\nYou requested a password reset. Click the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        return Response({"reset_url": reset_url})


# 비밀번호 재설정 링크
# 토큰 유효성 검증을 통해 비밀번호를 변경할 수 있습니다.
class PasswordResetConfirmView(APIView):
    """
    사용자가 이메일을 통해 받은 링크로 비밀번호를 재설정하는 뷰입니다.
    """

    @swagger_auto_schema(
        operation_description="비밀번호 재설정 API - 비밀번호 재설정 링크를 통해 비밀번호를 변경",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: "패스워드가 변경되었습니다",
            400: "Bad Request",
            404: "Not Found",
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = request.data.get("token")
        new_password = serializer.validated_data["password"]

        try:
            # 토큰을 검증하고 사용자를 찾습니다.
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(id=payload["id"], email=payload["email"]).first()
        if not user:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # 사용자의 비밀번호를 재설정합니다.
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset successfully."})


# 닉네임 및 프로필 이미지 업데이트
class NicknameAndProfileImageView(APIView):
    """
    사용자가 자신의 닉네임과 프로필 이미지를 업데이트할 수 있는 뷰입니다.
    """

    parser_classes = [
        MultiPartParser
    ]  # 파일 업로드를 처리하기 위해 MultiPartParser를 사용합니다.

    @swagger_auto_schema(
        operation_description="닉네임 및 프로필 이미지 변경 API - JWT 토큰을 통해 인증된 사용자만 사용 가능. 요청 데이터에서 새로운 닉네임과 프로필 이미지를 받아 업데이트합니다.",
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_FORM,
                description="새로운 닉네임",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "profile_image",
                openapi.IN_FORM,
                description="새로운 프로필 이미지 파일",
                type=openapi.TYPE_FILE,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="닉네임 및 프로필 이미지가 성공적으로 업데이트되었습니다.",
                examples={
                    "application/json": {
                        "detail": "Nickname and profile image updated successfully."
                    }
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def put(self, request):
        """
        사용자가 자신의 닉네임과 프로필 이미지를 업데이트할 수 있는 API입니다.
        """
        token = request.COOKIES.get("jwt")
        if not token:
            return Response(
                {"detail": "인증 자격 증명이 제공되지 않았습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["id"])
        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "토큰이 만료되었습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "사용자를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_nickname = request.data.get("nickname")
        new_profile_image = request.FILES.get("profile_image")

        if not new_nickname:
            return Response(
                {"detail": "새로운 닉네임은 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 닉네임 중복 확인 (현재 사용자 제외)
        if User.objects.filter(nickname=new_nickname).exclude(id=user.id).exists():
            return Response(
                {"detail": "이미 존재하는 닉네임입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 사용자의 닉네임을 업데이트합니다.
        user.nickname = new_nickname

        # 프로필 이미지가 있으면 저장합니다.
        if new_profile_image:
            user.profile_image = new_profile_image

        user.save()

        # 업데이트된 사용자 정보를 반환합니다.
        serializer = UserSerializer(user)
        return Response(
            {
                "detail": "닉네임 및 프로필 이미지가 성공적으로 업데이트되었습니다.",
                "user": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
