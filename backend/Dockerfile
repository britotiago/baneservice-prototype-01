# Dockerfile for Backend
FROM python:3.10-slim

# Install required libraries
RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./backend /app

# Copy assets directory
COPY ./assets /app/assets

# Ensure the 'wait-for-db.sh' script is executable
RUN chmod +x /app/wait-for-db.sh

# Collect static files if necessary
RUN python manage.py collectstatic --noinput

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["/app/wait-for-db.sh"]
