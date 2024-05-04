FROM archlinux:latest

# Install dependencies
RUN pacman -Syyu --noconfirm
RUN pacman -S --noconfirm base-devel git cmake
RUN pacman -S --noconfirm python python-pip redis
RUN redis-server --daemonize yes

# Set WORKDIR
WORKDIR /app

# Copy the source code
COPY . /app

# Install the python dependencies
RUN pip install -r requirements.txt --break-system-packages

# Run migrations and collect static files
RUN python manage.py migrate

# Run redis
CMD ["celery", "-A", "core.celery_app", "worker", "--beat", "--loglevel=info"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# Run the application
