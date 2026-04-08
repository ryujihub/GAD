# Use the official Playwright Python image
# This image comes with Python and all necessary system dependencies for Playwright
FROM mcr.microsoft.com/playwright/python:v1.51.0-noble

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set the working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure necessary directories exist
RUN mkdir -p data static scripts

# Install chromium specifically to be sure, although it's usually in the base image
# We use --with-deps just in case, though the base image covers it.
RUN playwright install chromium

# Start gunicorn with explicit shell for environment variable expansion
CMD ["sh", "-c", "gunicorn app:app --workers 2 --bind 0.0.0.0:${PORT:-8080}"]
