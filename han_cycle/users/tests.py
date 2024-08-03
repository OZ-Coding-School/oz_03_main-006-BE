import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import RefreshToken
import jwt
import datetime
from django.conf import settings

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return _create_user

@pytest.fixture
def user_data():
    return {
        'nickname': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    }

@pytest.fixture
def auth_headers(create_user, user_data):
    user = create_user(**user_data)
    client = APIClient()
    response = client.post(reverse('login'), {
        'nickname': user_data['nickname'],
        'password': user_data['password']
    }, format='json')
    jwt_token = response.cookies['jwt'].value
    refresh_token = response.cookies['refresh_token'].value
    return {
        'HTTP_AUTHORIZATION': f'Bearer {jwt_token}',
        'HTTP_REFRESH_TOKEN': refresh_token,
    }

@pytest.mark.django_db
def test_register_user(api_client, user_data):
    response = api_client.post(reverse('register'), user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.count() == 1
    assert User.objects.get().nickname == 'testuser'

@pytest.mark.django_db
def test_login_user(api_client, create_user, user_data):
    create_user(**user_data)
    response = api_client.post(reverse('login'), {
        'nickname': user_data['nickname'],
        'password': user_data['password']
    }, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'jwt' in response.cookies
    assert 'refresh_token' in response.cookies

@pytest.mark.django_db
def test_get_user_details(api_client, create_user, user_data, auth_headers):
    user = create_user(**user_data)
    api_client.credentials(HTTP_AUTHORIZATION=auth_headers['HTTP_AUTHORIZATION'])
    response = api_client.get(reverse('user'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nickname'] == user.nickname

@pytest.mark.django_db
def test_logout_user(api_client, create_user, user_data, auth_headers):
    user = create_user(**user_data)
    api_client.credentials(HTTP_AUTHORIZATION=auth_headers['HTTP_AUTHORIZATION'])
    response = api_client.post(reverse('logout'))
    assert response.status_code == status.HTTP_200_OK
    assert 'jwt' not in response.cookies
    assert 'refresh_token' not in response.cookies

@pytest.mark.django_db
def test_delete_account(api_client, create_user, user_data, auth_headers):
    user = create_user(**user_data)
    api_client.credentials(HTTP_AUTHORIZATION=auth_headers['HTTP_AUTHORIZATION'])
    response = api_client.delete(reverse('delete-account'))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.count() == 0

@pytest.mark.django_db
def test_password_reset_request(api_client, create_user, user_data):
    user = create_user(**user_data)
    response = api_client.post(reverse('password-reset-request'), {
        'email': user.email
    }, format='json')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_password_reset_confirm(api_client, create_user, user_data):
    user = create_user(**user_data)
    payload = {
        "id": user.id,
        "email": user.email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    response = api_client.post(reverse('password-reset-confirm'), {
        'token': token,
        'password': 'newpassword123'
    }, format='json')
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password('newpassword123')

@pytest.mark.django_db
def test_edit_nickname_and_profile_image(api_client, create_user, user_data, auth_headers):
    user = create_user(**user_data)
    api_client.credentials(HTTP_AUTHORIZATION=auth_headers['HTTP_AUTHORIZATION'])
    with open('path/to/your/test/image.jpg', 'rb') as image:
        response = api_client.put(reverse('edit'), {
            'nickname': 'newnickname',
            'profile_image': image
        }, format='multipart')
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.nickname == 'newnickname'
    assert user.profile_image is not None
