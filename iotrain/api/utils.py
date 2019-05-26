import os
from functools import wraps
from logging import getLogger

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
logger = getLogger("app")
logger.setLevel(LOG_LEVEL)


def logging(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        logger.debug(
            "{func}({args}, {kwds}):".format(
                func=func.__qualname__, args=str(args), kwds=kwds
            )
        )
        result = func(*args, **kwds)
        logger.debug("{func} -> {result}".format(func=func.__qualname__, result=result))
        return result

    return wrapper
