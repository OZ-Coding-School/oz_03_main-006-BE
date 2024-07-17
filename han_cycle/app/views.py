from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth.decorators import login_required


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


@login_required
def profile_view(request):
    context = {
        'user': request.user
    }
    return render(request, 'profile.html', context)