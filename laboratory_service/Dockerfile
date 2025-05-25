FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for PostgreSQL and networking tools
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    pkg-config \
    build-essential \
    gcc \
    python3-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run entrypoint script
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
