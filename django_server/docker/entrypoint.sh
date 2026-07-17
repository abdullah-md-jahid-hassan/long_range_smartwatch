
# entrypoint.sh

#!/bin/sh
set -e

# Ensure virtualenv is active
export PATH="/venv/bin:$PATH"

# Only web container should run migrations & collectstatic
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Making migration files..."
    python manage.py makemigrations

    echo "Applying database migrations..."
    python manage.py migrate --noinput

    # echo "Collecting static files..."
    # python manage.py collectstatic --noinput || true
fi

# Execute passed command (gunicorn / celery)
exec "$@"
