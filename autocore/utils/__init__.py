import logging
import os
import platform
import random
import sys
import time
import traceback

from assertpy import assert_that, assert_warn
from getgauge.python import Messages, Screenshots, data_store
from loguru import logger

# ================= Common methods =================

# __current_path = os.path.abspath(__file__)
# PROJECT_PATH = get_ancestor_path(__current_path, level=3)
os_name = platform.system()  # Mac: Darwin | Win: Windows | Linux: Linux
logger.remove()
customize_format = "\t<level>{time:DD-MM-YYYY HH:mm:ss.SSS}</level> <level>[{file}:{line}] [{level}] {message}</level>"
# logger.add(sys.stderr, colorize=True, format=customize_format)
logger.add(sys.stdout, colorize=True, format=customize_format)


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        try:
            return f(*args, **kwargs)
        except Exception:
            pass
        finally:
            time2 = time.time()
            logger.debug(f'Function "{f.__name__:s}" took {(time2 - time1):,.3f} seconds !!!')

    return wrap


def gauge_wrap(f):
    def wrap(*args, **kwargs):
        start = time.time()

        try:
            return f(*args, **kwargs)
        except Exception:
            pass
        finally:
            if not hasattr(data_store.suite, "license") or not data_store.suite.license:
                while (time.time() - start) < (random.randint(0, 10) / 10):
                    pass

    return wrap


def get_parent_path(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def get_ancestor_path(path, level=1):
    level = level if level >= 0 else 1
    for _ in range(level):
        path = get_parent_path(path)
    return path


# ================= Example Using Assert lib =================


def example_assert_that():
    logger.debug("Test example_assert_that")
    assert_that("Actual").is_equal_to("Expected")


def example_assert_warn():
    logger.debug("Test example_assert_warn")
    assert_warn("Actual", description="Description is here", logger=logger).is_equal_to("Expected")
