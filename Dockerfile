FROM archlinux:latest

# Install system dependencies
RUN pacman -Syyu --noconfirm python python-pip redis

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy the Django project code
COPY . .

# Run migrations and collect static files
RUN python manage.py migrate

# Expose the port for Django
EXPOSE 8000

# Start Redis and Celery worker
CMD redis-server --daemonize yes && \
    celery -A core.celery_app worker --beat --loglevel=info & \
    python manage.py runserver 0.0.0.0:8000