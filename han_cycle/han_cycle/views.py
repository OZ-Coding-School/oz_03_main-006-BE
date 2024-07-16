from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated

class UserAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

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


def profile_view(request):
    # Access the user object from the request
    user = request.user

    # Retrieve profile data based on the user
    # (Replace with your logic to get relevant profile data)
    profile_data = {'username': user.username, 'email': user.email}

    context = {'profile_data': profile_data}
    return render(request, 'profile.html', context)