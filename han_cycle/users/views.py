
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime, requests
from django.conf import settings
from django.shortcuts import redirect, render
import os
from datetime import timedelta
import random
import string




class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise exception if the data is invalid
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        nickname = request.data['nickname']
        password = request.data['password']

        user = User.objects.filter(nickname=nickname).first()  # Login is possible if the password is correct

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }
        # Generate token
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        # Set the token in the cookie
        response.set_cookie(key='jwt', value=token, httponly=True, secure=True, samesite='Lax')

        # No token show up in response data body
        response.data = {
            'message': 'Successfully logged in'
        }

        return response

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Successfully logged out'
        }
        return response



# Social login callback views

def googleredirect(request):
    state = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    request.session['oauth_state'] = state
    return redirect(
        f'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={os.getenv("GOOGLE_CLIENT_ID")}&redirect_uri={os.getenv("GOOGLE_REDIRECT_URI")}&scope=openid%20email%20profile&state={state}'
    )

class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        if state != request.session.pop('oauth_state', None):
            return Response({'error': 'Invalid state'}, status=400)

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            'grant_type': 'authorization_code',
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI'),
            'code': code,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_response = requests.post(token_url, data=payload, headers=headers)

        try:
            token_json = token_response.json()
        except requests.exceptions.JSONDecodeError:
            return Response({'error': 'Invalid response from Google API'}, status=500)

        access_token = token_json.get('access_token')
        if not access_token:
            return Response({'error': 'Failed to get access token'}, status=400)

        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)

        try:
            user_info = user_info_response.json()
        except requests.exceptions.JSONDecodeError:
            return Response({'error': 'Invalid response from Google API'}, status=500)

        payload = {
            'user_id': user_info['id'],
            'exp': datetime.datetime.utcnow() + timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
        }
        jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

        response = redirect('/')
        response.set_cookie('jwt_token', jwt_token, httponly=True, secure=True, samesite='Lax')
        return response



def kakaoredirect(request):
    return redirect(f'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={os.getenv('KAKAO_CLIENT_ID')}&redirect_uri={os.getenv('KAKAO_REDIRECT_URI')}')

class KakaoLoginView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=400)

        # Exchange the authorization code for an access token
        token_url = "https://kauth.kakao.com/oauth/token"
        payload = {
            'grant_type': 'authorization_code',
            'client_id': os.getenv('KAKAO_CLIENT_ID'),
            'client_secret':os.getenv('KAKAO_CLIENT_SECRET'),
            'redirect_uri': os.getenv('KAKAO_REDIRECT_URI'),
            'code': code,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        token_response = requests.post(token_url, data=payload, headers=headers)

        try:
            token_json = token_response.json()
        except requests.exceptions.JSONDecodeError:
            return Response({'error': 'Invalid response from Kakao API'}, status=500)

        access_token = token_json.get('access_token')
        if not access_token:
            return Response({'error': 'Failed to get access token'}, status=400)

        # Use the access token to get user information from Kakao
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        user_info_response = requests.get(user_info_url, headers=headers)

        try:
            user_info = user_info_response.json()
        except requests.exceptions.JSONDecodeError:
            return Response({'error': 'Invalid response from Kakao API'}, status=500)

        # Create a JWT token for your application
        payload = {
            'user_id': user_info['id'],
            'exp': datetime.datetime.utcnow() + timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
        }
        jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

        # Set the JWT token in a cookie and redirect to frontend
        response = redirect('/')  # Replace with your frontend URL
        response.set_cookie('jwt_token', jwt_token, httponly=True, secure=True, samesite='Lax')

        return response
    