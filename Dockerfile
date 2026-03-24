FROM python:3.13-slim

# Prevent Python from writing .pyc files & keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working area inside the container
WORKDIR /app

# Install system dependencies needed for compiling psycopg2 (Postgres driver)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (to cache the Python dependencies layer)
COPY requirements.txt .

# Install Python packages
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Security best practice: Create a non-root user
RUN adduser --disabled-password --no-create-home botuser \
    && chown -R botuser:botuser /app
USER botuser

# Default command to run the bot
CMD ["python", "-m", "src.main"]
