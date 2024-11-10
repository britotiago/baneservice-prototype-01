#!/bin/sh

# Wait until Postgres is ready
echo "Waiting for Postgres at $DB_HOST:$DB_PORT with user $DB_USER..."
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - running migrations"
python manage.py migrate

# Check for populate_database.py and run it if available
POPULATE_SCRIPT="/app/baneservice/populate_database.py"
if [ -f "$POPULATE_SCRIPT" ]; then
  echo "Found $POPULATE_SCRIPT, proceeding with data population"
  if python "$POPULATE_SCRIPT"; then
    echo "Data population completed successfully."
  else
    echo "Warning: Data population encountered issues. Please check for missing columns or file paths."
  fi
else
  echo "Warning: $POPULATE_SCRIPT not found. Skipping data population."
fi

echo "Starting Gunicorn server"
exec gunicorn -b 0.0.0.0:8000 --timeout 120 -k gevent baneservice.wsgi:application

