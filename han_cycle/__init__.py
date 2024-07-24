# han_cycle/__init__.py

from __future__ import absolute_import, unicode_literals

# 이 패키지가 로드될 때 Celery 애플리케이션을 로드합니다.
from .celery import app as celery_app

__all__ = ("celery_app",)
