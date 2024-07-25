# Python 3.11이 설치된 Alpine Linux 3.19
FROM python:3.11-alpine3.19

# LABEL 명령어는 이미지에 메타데이터를 추가합니다.
LABEL maintainer="han_cycle"

# 환경 변수 PYTHONUNBUFFERED를 1로 설정합니다. 
ENV PYTHONUNBUFFERED=1

# 로컬 파일 시스템의 requirements.txt 파일을 컨테이너의 /tmp/requirements.txt로 복사합니다. 
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./han_cycle /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false

# 패키지 설치 및 파이썬 패키지 설치
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev netcat-openbsd && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    apk del gcc musl-dev libffi-dev python3-dev && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home django-user && \
    apk add --no-cache openrc && \
    rc-status && \
    touch /run/openrc/softlevel && \
    apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone && \
    apk del tzdata

# crontab 파일을 추가하고 권한 설정
COPY ./crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab && \
    crontab /etc/cron.d/crontab

# 스크래핑
RUN pip install requests beautifulsoup4

ENV PATH="/py/bin:$PATH"

USER django-user

# 실행 명령어
CMD ["sh", "-c", "crond && python manage.py runserver 0.0.0.0:8000"]