#!/bin/bash

set -e

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
cp -r /app/collected_static/. /backend_static/

gunicorn foodgram_backend.wsgi:application \
  --bind 0.0.0.0:8000