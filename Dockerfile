# 사용할 베이스 이미지
FROM python:3.11-alpine3.19

LABEL maintainer="han_cycle"

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=app.settings

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements.dev.txt /app/requirements.dev.txt

# 사용자 추가 (가상 환경 설치 전에 사용자 추가)
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

# 가상 환경 디렉토리 생성 및 권한 설정
RUN mkdir -p /home/django-user/.venv
RUN chown -R django-user:django-user /home/django-user/.venv

# 가상 환경 생성 및 의존성 패키지 설치
USER django-user
RUN python -m venv /home/django-user/.venv
ENV PATH="/home/django-user/.venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install python-decouple
RUN pip install -r /app/requirements.txt 
RUN if [ $DEV = "true" ]; \
        then pip install -r /app/requirements.dev.txt ; \
    fi
USER root  # root 사용자로 전환

# 프로젝트 파일 복사
COPY ./han_cycle /app

# django-user 사용자로 변경
USER django-user
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
