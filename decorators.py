import functools, time, logging

log = logging.getLogger(__name__)

def retry(times = 3, delay = 2.0, exceptions = (OSError,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    time.sleep(min(delay * 2 ** (attempt - 1), 20))
                    log.warning("%s failed (%s), attempt %d/%d", func.__name__, e, attempt, times)
            return None

        return wrapper
    return decorator
