# han_cycle/celery.py

import os

from celery import Celery
from django.conf import settings

# Django 설정 파일을 로드합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "han_cycle.app.settings")

app = Celery("han_cycle")  # Celery 앱 인스턴스 생성
app.config_from_object("django.conf:settings", namespace="CELERY")  # Celery 설정 로드
app.autodiscover_tasks()  # Django 앱에서 Celery task를 자동으로 검색


def debug_task(self):
    print(f"Request: {self.request!r}")
