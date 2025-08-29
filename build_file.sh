#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt --target="$VERCEL_OUTPUT"

echo "=== Setting environment variables ==="
export DJANGO_SETTINGS_MODULE=projectname.settings  # replace with your settings module
export PYTHONPATH=$PWD

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Build complete ==="
