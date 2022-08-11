#! /usr/bin/env python3
"""
Sorting component of the sorting system
* Waits for an image with a computed average RGB
* Sorts (puts it in a named folder) image file based on the average RGB
"""
import logging
import os

from kombu import Connection, Exchange, Queue

from config import Config

with open(Config.LOG_FILE, 'w'):
    pass  # clear the logfile on each restart
logging.basicConfig(filename=Config.LOG_FILE)
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

sort_queue = Queue(Config.SORT_QUEUE, durable=False)


def main():
    logger.info("""
+-------------------+
|  STARTING SORTER  |
+-------------------+
""")

    def callback(body, message):
        logger.debug(f"RECEIVED: {body}")
        if not os.path.isdir(Config.SORT_ROOT_PATH):
            os.mkdir(Config.SORT_ROOT_PATH)
        logger.debug(f"Sorting into: {Config.SORT_ROOT_PATH}")

    with Connection(Config.BROKER_URL) as receive_conn:
        with receive_conn.Consumer(sort_queue, callbacks=[callback]):
            while True:
                receive_conn.drain_events()


if __name__ == "__main__":
    main()
