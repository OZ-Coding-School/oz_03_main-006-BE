import datetime
from rest_framework.permissions import BasePermission, IsAuthenticated
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import RefreshToken
from .serializers import UserSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer
from django.urls import reverse
from django.core.mail import send_mail


User = get_user_model()

#회원가입으로 사용자 생성
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

#로그인 (닉네임과 비밀번호로 사용자 인증)
class LoginView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(type=openapi.TYPE_STRING, description="User nickname"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
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
                    }
                },
            ),
            400: "Bad Request",
            401: "Authentication Failed",
        },
    )
    # jwt 및 리프레시 토큰 생성
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

        # 엑세스 토큰 생성
        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow(),
        }
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        # 리프레쉬 토큰 생성
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        refresh_token = RefreshToken.objects.create(user=user, expires_at=expires_at)

        # JWT 토큰은 HTTP-only 쿠키에 세팅 (유효기간 설정)
        response = Response(
            {
                "id": user.id,
                "nickname": user.nickname,
                "profile_image": user.profile_image.url if user.profile_image else None,
                "email": user.email,
                "username": user.username,
            }
        )
        response.set_cookie(key="jwt", value=access_token, httponly=True, expires=datetime.datetime.utcnow() + datetime.timedelta(days=7))
        response.set_cookie(key="refresh_token", value=str(refresh_token.token), httponly=True, expires=expires_at)

        return response

#사용자 정보 조회
class UserView(APIView):
    @swagger_auto_schema(responses={200: UserSerializer, 401: "Unauthenticated"})
    def get(self, request):
        """
        사용자 정보 조회 API
        - JWT 토큰을 통해 인증된 사용자 정보 반환
        """
        token = request.COOKIES.get("jwt")
    # JWT 토큰 검증을 통해 사용자 정보 조회
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
#JWT 및 리프레쉬 토큰 쿠키 삭제
class LogoutView(APIView):
    @swagger_auto_schema(responses={200: "Successfully logged out"})
    def post(self, request):
        """
        로그아웃 API
        - JWT 토큰 삭제
        """
        response = Response()
        response.delete_cookie("jwt")
        response.delete_cookie("refresh_token")
        response.data = {"message": "Successfully logged out"}
        return response

#리프레쉬 토큰 (엑세스 토큰 재발급)
class RefreshTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="새로운 액세스 토큰을 발급하는 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="리프레시 토큰"),
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

#쿠키 인증 (비밀번호 재설정을 위한 토큰 인증)
class CookieAuthentication(BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get('jwt')
        if not token:
            return False
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = User.objects.get(id=payload['id'])
            return True
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(_('Token has expired.'))
        except jwt.InvalidTokenError:
            raise AuthenticationFailed(_('Invalid token.'))
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found.'))

        return False

# 계정 삭제 (JWT 쿠키 및 사용자 계정 삭제)
class DeleteAccountView(APIView):
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
        회원 탈퇴 API
        - JWT 토큰을 통해 인증된 사용자만 사용 가능
        - 인증된 사용자의 계정을 삭제합니다.
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
                {"detail": "토큰이 만료되었습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "유효하지 않은 토큰입니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        response = Response(
            {"detail": "계정이 성공적으로 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )
        response.delete_cookie("jwt")

        return response

#비밀번호 재설정 요청

class PasswordResetRequestView(APIView):
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

        # Prepare the email
        subject = "Password Reset Request"
        message = f"Hello,\n\nYou requested a password reset. Click the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Send the email
        send_mail(subject, message, from_email, recipient_list)

        return Response({"reset_url": reset_url})


#비밀번호 재설정 링크
#토큰 유효성 검증으로 비밀번호 변경 가능
class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(
        operation_description="비밀번호 재설정 API - 비밀번호 재설정 링크를 통해 비밀번호를 변경",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: "Password reset successful",
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
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=payload["id"], email=payload["email"]).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset successfully."})

#닉네임 및 프로필 이미지 업데이트
class NicknameAndProfileImageView(APIView):
    @swagger_auto_schema(
        operation_description="닉네임 및 프로필 이미지 변경 API - JWT 토큰을 통해 인증된 사용자만 사용 가능. 요청 데이터에서 새로운 닉네임과 프로필 이미지를 받아 업데이트합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 닉네임"
                ),
                "profile_image": openapi.Schema(
                    type=openapi.TYPE_STRING, description="새로운 프로필 이미지 URL"
                ),
            },
            required=["nickname"],
        ),
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
        new_profile_image = request.data.get("profile_image")

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

        if new_profile_image:
            user.profile_image = new_profile_image

        user.save()

        return Response(
            {"detail": "Nickname and profile image updated successfully."},
            status=status.HTTP_200_OK,
        )
