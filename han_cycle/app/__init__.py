# han_cycle/__init__.py

from .celery import app as celery_app  # Celery 앱 import

__all__ = ("celery_app",)  # 외부에서 Celery 앱을 사용할 수 있도록 설정
