from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from rest_framework import status
from .serializers import RegistrationSerializer, UserSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from .renderers import UserJSONRenderer

#로그인 성공시 프로필 페이지

@login_required
def ProfileView(request):
    return render(request, 'profile.html')

class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer
    
    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        serializer_data = request.data
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

#recieve information with token
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated()
        return Response({          
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "profile_image": user.profile_image
        }) 

#recieve token with sign in
    def post(self, request):
        username = request.data.get("username","")
        password = request.data.get("password","")

        if (username and password):
            if User.objects.filter(username=username).exists():
                return Response({
                    "error": "A user with that username exists",
                }, status=401)
            user = User.objects.create(username=username, password=password)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                'access': str(refresh.access_token),
            }, status=201)
        
        return Response({
            "error": "Both username and password must be provided."
        })


