Celery + Redis setup
--------------------

1) Install Python dependencies (recommend adding to `requirements.txt`):

```bash
pip install "celery>=5.2,<6" "redis>=4.0,<6"
# optional: pip install django-celery-beat django-celery-results
```

2) Run Redis (local development):

On Windows, install Redis or use WSL / Docker. With Docker:

```bash
docker run -p 6379:6379 -d --name redis redis:7
```

3) Start a Celery worker from the project root:

```bash
# activate virtualenv
celery -A mysite worker --loglevel=info
```

4) Optional: start Celery beat for scheduled tasks

```bash
celery -A mysite beat --loglevel=info
```

5) Example: enqueue a logging task from Django shell or views

```python
from accounts.tasks import log_event
log_event.delay('info', 'Candidate matched', {'job_id': 123})
```

6) Logs are written to `logs/celery.log` (create `logs/` directory if needed).
