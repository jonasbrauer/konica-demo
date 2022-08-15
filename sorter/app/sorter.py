import base64
import io
import json
import os
from contextlib import contextmanager

import pika as pika
from PIL import Image, UnidentifiedImageError

from app import get_logger

log = get_logger(__name__)


class SorterError(Exception):
    pass


class Sorter:

    def __init__(self) -> None:
        self.queue_name = None  # dynamic queue, created & bound on start-up

        self.target_dir = os.environ.get("TARGET_DIR")
        self.broker_host = os.environ.get("BROKER_HOST")
        self.broker_port = os.environ.get("BROKER_PORT") or 5672
        self.input_exchange = os.environ.get("INPUT_EXCHANGE")
        self.topic = "#"  # handle all messages from the exchange

        self.setup_target_dir()

    def setup_target_dir(self):
        if not self.target_dir:
            raise SorterError("Target directory is not configured.")
        if os.path.isfile(self.target_dir):
            raise SorterError(f"Target directory {self.target_dir} is a file.")
        os.makedirs(self.target_dir, exist_ok=True)

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

    @staticmethod
    def _validate_body(body):
        required_fields = ("image", "id", "rgb")
        try:
            body = json.loads(body)
        except Exception as e:
            raise SorterError(e)

        for field in required_fields:
            if not body.get(field):
                raise SorterError(f"'{field}' field missing in message body: {body}")
        return body

    @staticmethod
    def _validate_image(image_data_b64_string) -> Image:
        """Use pillow to verify if the received data is an actual image."""
        image_bytes = base64.b64decode(image_data_b64_string.encode())
        stream = io.BytesIO(image_bytes)
        try:
            image = Image.open(stream)
            image.getexif()
        except UnidentifiedImageError as e:
            raise SorterError("Invalid image data", e)

        if not image.format:
            raise SorterError("Unknown image format.")

        log.debug(f"'{image.format}' image loaded: {image.height}x{image.width}")
        return image

    def sort(self, image_name: str, image_color: str, image: Image) -> None:
        """Sort/save image in a subdir based on the supplied hex color value."""
        log.debug(f"Sorting image {image.height}x{image.width} with RGB: {image_color}")
        target_color_dir_path = os.path.join(self.target_dir, image_color)
        os.makedirs(target_color_dir_path, exist_ok=True)
        final_path = os.path.join(target_color_dir_path, image_name) + f".{image.format}"
        log.info(f"Saving: {final_path}")
        image.save(final_path)

    def sort_callback(self, body):
        body = self._validate_body(body)
        image = self._validate_image(body["image"])
        self.sort(
            image_name=body["id"],
            image_color=body["rgb"],
            image=image
        )

    def start_listening(self):
        with self.connection() as connection:
            channel = connection.channel()
            channel.exchange_declare(self.input_exchange, exchange_type="topic")
            result = channel.queue_declare("", exclusive=True)
            self.queue_name = result.method.queue
            channel.queue_bind(
                exchange=self.input_exchange,
                queue=self.queue_name,
                routing_key=self.topic
            )

            def callback(chan, method, properties, body):
                try:
                    self.sort_callback(body)
                except Exception as e:
                    # log the exception and carry on
                    log.error("Message handling failed.", exc_info=e)

            channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            log.info("Waiting for images to be sorted... To exit press CTRL+C")
            log.debug(
                f"Consuming: exchange={self.input_exchange}, "
                f"topic={self.topic}, queue={self.queue_name}"
            )
            channel.start_consuming()
