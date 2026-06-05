web: gunicorn mysite.wsgi --log-file -
worker: gunicorn mysite.wsgi --log-file - & celery -A mysite worker --loglevel=info