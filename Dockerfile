FROM python:3.12-alpine
LABEL maintainer="iscenkoa@gmail.com"

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies for Python builds and Chrome
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    postgresql-client \
    # chromium \
    # chromium-chromedriver \
    curl \
    bash

RUN addgroup -S celerygroup && adduser -S celeryuser -G celerygroup

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/dumps && chown -R celeryuser:celerygroup /app
RUN mkdir -p /app/logs && chown -R celeryuser:celerygroup /app
RUN chmod -R 777 /app/logs
RUN touch /app/logs/scraper.log && chmod 666 /app/logs/scraper.log && chown celeryuser:celerygroup /app/logs/scraper.log


COPY . .


USER celeryuser

# Set default command
CMD ["celery", "-A", "app.scraper.tasks", "worker", "--loglevel=info"]