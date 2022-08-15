import os
import logging
import sys
import uuid


def get_logger(name: str):
    log_level = os.environ.get('LOG_LEVEL') or logging.INFO
    log_file = os.environ.get('LOG_FILE')

    log_format = '[%(asctime)s] %(levelname)s\t[%(name)s] %(message)s'
    logger = logging.getLogger(name)

    logger.setLevel(log_level)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    if log_file:
        file_handler = logging.FileHandler(filename=os.environ['LOG_FILE'], mode='a')
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    return logger


def generate_uuid():
    return str(uuid.uuid4())
