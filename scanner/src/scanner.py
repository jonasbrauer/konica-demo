import base64
import json
import logging
import os
import random
import time
from contextlib import contextmanager

import pika


class ScannerError(Exception):
    pass


class Scanner:

    def __init__(self, config) -> None:
        self.scan_dirs = config.SCAN_DIRS
        self.logfile = config.LOG_FILE
        self.broker_host = config.BROKER_HOST
        self.broker_port = config.BROKER_PORT
        self.compute_exchange = config.COMPUTE_QUEUE

        # log to a separate file
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.DEBUG)
        handler = logging.FileHandler(self.logfile, mode="w")
        formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)

    @contextmanager
    def connection(self) -> pika.BlockingConnection:
        self.log.debug(f"Starting connection for: {self.broker_host}:{self.broker_port}")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.broker_host,
                port=self.broker_port,
                connection_attempts=5,
                retry_delay=2,
            )
        )
        try:
            yield connection
        except Exception as e:
            self.log.error('MQ connection failed', exc_info=e)
        finally:
            connection.close()

    def scan(self, directory: str) -> list:
        image_data = random.randbytes(12)
        self.log.debug(f"Read new image from {directory}: {image_data}")
        return [image_data]

    def publish_image(self, image_data: bytes) -> None:
        uuid = base64.b64encode(os.urandom(32)[:8]).decode()
        self.log.debug(f"Publishing image {uuid}")
        body = {
            'id': uuid,
            'image': base64.b64encode(image_data).decode(),
        }
        with self.connection() as conn:
            channel = conn.channel()
            channel.basic_publish(
                exchange=self.compute_exchange,
                routing_key='compute',
                body=json.dumps(body).encode(),
            )

    def start_scanning(self):
        # setup
        with self.connection() as conn:
            channel = conn.channel()
            channel.exchange_declare(exchange=self.compute_exchange, exchange_type='direct')

        # loop
        self.log.info("Scanning loop started. To exit press CTRL+C")
        while True:
            for directory in self.scan_dirs:
                new_images = self.scan(directory)
                for image in new_images:
                    self.publish_image(image)
            time.sleep(10)
