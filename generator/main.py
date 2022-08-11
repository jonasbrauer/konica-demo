#! /usr/bin/env python3
"""
Generator component of the sorting system
* Scans a given directory for file changes
* On a 'change detected' reads the image and sends it to the broker
"""
import logging
import random

import pika
import time

from config import Config


with open(Config.LOG_FILE, 'w'):
    pass  # clear the logfile on each restart
logging.basicConfig(filename=Config.LOG_FILE)
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


def read_image():
    image_data = random.randbytes(12)
    logger.debug(f"Read new image: {image_data}")
    return image_data


if __name__ == "__main__":
    logger.info("""
+----------------------+
|  STARTING GENERATOR  |
+----------------------+
""")

    i = 0
    while True:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.BROKER_HOST,
                port=Config.BROKER_PORT,
                connection_attempts=5,
                retry_delay=5,
            )
        )
        channel = connection.channel()

        channel.queue_declare(queue=Config.COMPUTE_QUEUE)

        channel.basic_publish(
            exchange="",
            routing_key=Config.COMPUTE_QUEUE,
            body=read_image()
        )

        connection.close()
        logger.debug("Connection closed, sleeping...")
        time.sleep(10)
