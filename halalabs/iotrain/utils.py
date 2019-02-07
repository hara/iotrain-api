import logging
import os
from functools import wraps

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
_streamHandler = logging.StreamHandler()
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
_streamHandler.setFormatter(_formatter)
logger.addHandler(_streamHandler)


def logging(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        logger.debug('{func}({args}, {kwds}):'.format(
            func=func.__qualname__, args=str(args), kwds=kwds))
        result = func(*args, **kwds)
        logger.debug('{func} -> {result}'.format(
            func=func.__qualname__, result=result))
        return result

    return wrapper
