# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/
RUN chmod +x /app/start.sh

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Run collectstatic
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the application using Gunicorn (for production)
CMD ["/app/start.sh"]
