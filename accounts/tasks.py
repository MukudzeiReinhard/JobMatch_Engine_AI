import logging
from celery import shared_task

logger = logging.getLogger('tasks')


@shared_task(bind=True)
def log_event(self, level: str, message: str, extra: dict | None = None) -> dict:
    """Generic logging task for asynchronous logging of events.

    Args:
        level: 'info'|'warning'|'error'
        message: message to log
        extra: optional dict passed to the logger as extra

    Returns:
        dict with status
    """
    extra = extra or {}
    try:
        if level == 'info':
            logger.info(message, extra=extra)
        elif level == 'warning':
            logger.warning(message, extra=extra)
        else:
            logger.error(message, extra=extra)
        return {'status': 'logged', 'level': level}
    except Exception as exc:
        logger.exception('Failed to log event: %s', exc)
        # Reraise if you want Celery to register a failure, or return error state
        raise
