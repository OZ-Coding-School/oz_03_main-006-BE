from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime

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
