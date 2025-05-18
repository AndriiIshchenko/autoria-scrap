FROM python:3.12-alpine
LABEL maintainer="iscenkoa@gmail.com"

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies for Python builds and PostgreSQL tools
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev postgresql-client

# Create a non-root user
RUN addgroup -S celerygroup && adduser -S celeryuser -G celerygroup

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create dumps directory and set permissions
RUN mkdir -p /app/dumps && chown -R celeryuser:celerygroup /app

# Copy application code
COPY . .

# Switch to the non-root user
USER celeryuser

# Set default command (can be overridden by docker-compose)
CMD ["celery", "-A", "app.scraper.tasks", "worker", "--loglevel=info"]