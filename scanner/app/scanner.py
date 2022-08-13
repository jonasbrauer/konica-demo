import base64
import json
import os
import time
from contextlib import contextmanager

import pika

from app import get_logger, generate_uuid

log = get_logger(__name__)


class ScannerError(Exception):
    pass


class Scanner:

    def __init__(self) -> None:
        self.scan_dirs = os.environ.get("SCAN_DIRS")
        self.broker_host = os.environ.get("BROKER_HOST")
        self.broker_port = os.environ.get("BROKER_PORT") or 5672
        self.output_exchange = os.environ.get('OUTPUT_EXCHANGE')
        self.output_routing_key = os.environ.get('OUTPUT_ROUTING_KEY') or "compute"

        if not self.scan_dirs:
            raise ScannerError("Directories to be scanned not configured.")
        self.scan_dirs = self.scan_dirs.split(",")

    @contextmanager
    def connection(self) -> pika.BlockingConnection:
        log.debug(f"Starting connection for: {self.broker_host}:{self.broker_port}")
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
            log.error(
                f"MQ connection (host={self.broker_host}, port={self.broker_port} failed",
                exc_info=e
            )
        finally:
            connection.close()

    @staticmethod
    def scan(directory: str) -> list:
        files = os.listdir(directory)
        log.debug(f"Scanning {directory}...")
        log.info(f"Found new image files: {files}")
        return [os.path.join(directory, file) for file in files]

    def publish_image(self, image_path: str) -> None:
        image_id = generate_uuid()
        log.debug(f"Reading/converting image {image_path}")
        with open(image_path, 'rb') as image:
            f = image.read()
            image_bytes = bytearray(f)

        log.debug(f"Publishing image id={image_id}")
        with self.connection() as conn:
            channel = conn.channel()
            channel.basic_publish(
                exchange=self.output_exchange,
                routing_key=self.output_routing_key,
                body=json.dumps({
                    'id': image_id,
                    'image': base64.b64encode(image_bytes).decode(),
                }).encode(),
            )
        log.debug(f"Sent, exchange={self.output_exchange}, key={self.output_routing_key}")

    def start_scanning(self):
        # 1) setup output exchange
        with self.connection() as conn:
            channel = conn.channel()
            channel.exchange_declare(exchange=self.output_exchange, exchange_type='direct')

        # 2) Start the loop
        log.info("Scanning loop started. To exit press CTRL+C")
        while True:
            for directory in self.scan_dirs:
                new_images = self.scan(directory)
                for image in new_images:
                    self.publish_image(image)
            time.sleep(60)
