import base64
import json
import os
import threading
import time
from contextlib import contextmanager

import pika

from app import get_logger, generate_uuid

log = get_logger(__name__)


class ScannerError(Exception):
    pass


class Scanner:

    def __init__(self) -> None:
        self.watch_dir = os.environ.get("WATCH_DIR")
        self.scan_interval = int(os.environ.get("SCAN_INTERVAL_SECS") or 5)

        self.broker_host = os.environ.get("BROKER_HOST")
        self.broker_port = os.environ.get("BROKER_PORT") or 5672
        self.output_exchange = os.environ.get('OUTPUT_EXCHANGE')
        self.output_routing_key = os.environ.get('OUTPUT_ROUTING_KEY') or "compute"

        self.exit_event = threading.Event()
        self.published_images = set()

        if not self.watch_dir:
            raise ScannerError("Directories to be scanned not configured.")

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
        finally:
            connection.close()

    def scan(self, directory: str) -> set:
        # TODO: scan recursively
        files = {os.path.join(directory, file) for file in os.listdir(directory)}
        files = {file for file in files if os.path.isfile(file)}
        return files.difference(self.published_images)

    def publish_image(self, image_path: str) -> None:
        image_id = generate_uuid()
        log.debug(f"Reading image {image_path}")
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
        self.published_images.add(image_path)

    def start_scanning(self):
        # 1) setup output exchange
        with self.connection() as conn:
            channel = conn.channel()
            channel.exchange_declare(exchange=self.output_exchange, exchange_type='direct')

        # 2) Start the loop
        log.info("Scanning loop started. To exit press CTRL+C")
        no_new_images_msg_displayed = False
        while True:
            # TODO: scan more than 1 directory
            new_images = self.scan(self.watch_dir)

            if new_images:
                log.info(f"New images found: {new_images}")
                no_new_images_msg_displayed = False
            elif not no_new_images_msg_displayed:
                log.info(f"No new images ({self.watch_dir})")
                no_new_images_msg_displayed = True

            for image in new_images:
                self.publish_image(image)

            time.sleep(self.scan_interval)
            if self.exit_event.is_set():
                break
