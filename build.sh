#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install all dependencies
pip install -r requirements.txt

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run database migrations automatically
python manage.py migrate