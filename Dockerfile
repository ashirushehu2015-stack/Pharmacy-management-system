# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Normalize line endings for start.sh and make it executable
RUN sed -i 's/\r$//' /app/start.sh && \
    chmod +x /app/start.sh

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Run collectstatic
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/start.sh"]
