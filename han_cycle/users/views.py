import datetime

import jwt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer, responses={201: UserSerializer, 400: "Bad Request"}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "jwt": openapi.Schema(
                        type=openapi.TYPE_STRING, description="JWT token"
                    )
                },
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    def post(self, request):
        nickname = request.data["nickname"]
        password = request.data["password"]

        user = User.objects.filter(nickname=nickname).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")

        payload = {
            "id": user.id,
            "exp": datetime.datetime.now() + datetime.timedelta(days=7),
            "iat": datetime.datetime.now(),
        }
        token = jwt.encode(payload, "secret", algorithm="HS256")

        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {"jwt": token}

        return response


class UserView(APIView):
    @swagger_auto_schema(responses={200: UserSerializer, 401: "Unauthorized"})
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated!")

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated!")

        user = User.objects.filter(id=payload["id"]).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Logout message"
                    )
                },
            )
        }
    )
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "successfully logged out"}
        return response
