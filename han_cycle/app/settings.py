"""
Django settings for han_cycle project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import time
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from retrying import retry

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

load_dotenv(override=True)
# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "43.203.170.167",
    "localhost",
    "127.0.0.1",
    "52.79.207.68",
    "43.202.53.249",
]

# 프론트 테스트용
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://hancycle.site",
]

# front-end ports to access our app
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True  # if it's false, front-end can't get cookie


# Retry configuration: 5 retries with exponential backoff (max wait 10 seconds)
@retry(
    stop_max_attempt_number=5,
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
)
def wait_for_elasticsearch():
    es = Elasticsearch(["http://elasticsearch:9200"])
    if not es.ping():
        raise ConnectionError("Elasticsearch server is not available")


# Call the wait function before Django starts
wait_for_elasticsearch()

# Application definition
INSTALLED_APPS = [
    "common",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "boards.apps.BoardsConfig",
    "locations",
    "users",
    # django-authentication apps
    "django.contrib.sites",
    "storages",
    "rest_framework",
    "social_django",
    "rest_framework.authtoken",
    "drf_yasg",
    "tinymce",
    "search",
    "django_crontab",
    "weather",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 스웨거 세팅, 커스텀유저 모델 허용가능으로 수정
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "DEFAULT_AUTO_SCHEMA_CLASS": "drf_yasg.inspectors.SwaggerAutoSchema",
    "USE_SESSION_AUTH": False,
}


# django-authentication
SITE_ID = 1
SOCIALACCOUNT_LOGIN_ON_GET = True

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "users" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Google
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Kakao
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# django-authentication
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    "social_core.backends.kakao.KakaoOAuth2",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "kakao": {
        "SCOPE": [
            "profile_nickname",
            "profile_image",
            "account_email",
        ]
    },
}

# backend check the login for test
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# make email is required for login
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_ADAPTER = "users.adapters.CustomSocialAccountAdapter"
LOGIN_REDIRECT_URL = "/users/accounts/profile/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

WSGI_APPLICATION = "app.wsgi.application"


# S3 setting
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

AWS_S3_CUSTOM_DOMAIN = "%s.s3.%s.amazonaws.com" % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME,
)

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "images"
AWS_DEFAULT_ACL = None

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Media settings
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# 엘라스틱서치 의존성
ELASTICSEARCH_DSL = {
    "default": {"hosts": "http://elasticsearch:9200"},
}

# 기상청 API요청
KMA_API_KEY = os.getenv("KMA_API_KEY")
# override default user django
AUTH_USER_MODEL = "users.User"
