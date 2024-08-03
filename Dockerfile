# Use Python 3.11 on Alpine Linux 3.19
FROM python:3.11-alpine3.19

# Add metadata to the image
LABEL maintainer="han_cycle"

# Set environment variable to ensure output is not buffered
ENV PYTHONUNBUFFERED=1

# Copy requirements files to the container
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy the application code to the container
COPY ./han_cycle /app

# Set the working directory
WORKDIR /app

# Expose the application port
EXPOSE 8000

# Set an argument to differentiate between development and production
ARG DEV=false

# Install dependencies and create a virtual environment
RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev netcat-openbsd tzdata && \
    cp /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    echo "Etc/UTC" > /etc/timezone && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi && \
    /py/bin/pip install requests && \
    apk del gcc musl-dev libffi-dev python3-dev && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home django-user

# Add and set up the crontab file
COPY ./crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab && \
    crontab /etc/cron.d/crontab

# Install additional dependencies
RUN pip install xmltodict

# Set the timezone
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# Add virtual environment to PATH
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user
USER django-user

# Default command to run the application
CMD ["sh", "-c", "crond && python manage.py runserver 0.0.0.0:8000"]
