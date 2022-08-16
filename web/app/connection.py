import base64
import json
import os
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta

import pika

from app.log import get_logger


class Computation:
    """
    An object representing a single computation request (single image),
    it is storing the image identifier, connection details as well as the message consumer thread.

    Modify behavior using these environment variables:
    * LOG_LEVEL
    * LOG_FILE
    * BROKER_HOST
    * BROKER_PORT (defaults to 5672)
    * OUTPUT_EXCHANGE: where to send the computation requests
    * OUTPUT_ROUTING_KEY: (defaults to 'compute')
    * INPUT_EXCHANGE: where to consume the result messages
    * INPUT_ROUTING_KEY: a topic suffix (defaults to 'computed'),
                         the actual topic will is in format: "<request_id>.<suffix>"
    """

    def __init__(self, image_bytes) -> None:
        self.broker_host = os.environ.get("BROKER_HOST")
        self.broker_port = os.environ.get("BROKER_PORT") or 5672
        self.output_exchange = os.environ.get('OUTPUT_EXCHANGE')
        self.output_routing_key = os.environ.get('OUTPUT_ROUTING_KEY') or "compute"
        self.input_exchange = os.environ.get("INPUT_EXCHANGE")
        self.topic_suffix = os.environ.get('INPUT_ROUTING_KEY') or "computed"

        # Ideally we of course don't want to keep the image bytes in memory,
        # e.g. we could use a mounted file system shared with the sorting service
        # and serve image data directly from there.
        self.image_bytes = image_bytes

        self.image_id = str(uuid.uuid4())  # track the request through the system
        self.queue_name = None  # ad-hoc queue
        self.running_thread = None
        self.result = None  # store resulting average RGB
        self.error = None  # store any errors
        # TODO: make compute service publish computation-related error messages as well
        # TODO: with "<image-id>.error" topic and display them.
        self.log = get_logger(self.image_id)

    @property
    def is_running(self):
        return self.running_thread is not None

    @property
    def data_size_kb(self):
        return len(self.image_bytes) / 1000

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
        finally:
            connection.close()

    @staticmethod
    def _validate_body(body) -> str:
        body = json.loads(body)
        if "rgb" not in body:
            raise ValueError("'rgb' field is missing.")
        return body["rgb"]

    def _create_queue(self, channel):
        channel.exchange_declare(self.input_exchange, exchange_type="topic")
        result = channel.queue_declare("", exclusive=True)
        self.queue_name = result.method.queue
        channel.queue_bind(
            exchange=self.input_exchange,
            queue=self.queue_name,
            routing_key=f"{self.image_id}.{self.topic_suffix}"
        )

    def _is_queue_empty(self, channel):
        # declaring an already existing queue to query information about it
        queue = channel.queue_declare(self.queue_name, exclusive=True, passive=True)
        return queue.method.message_count == 0

    def wait_for_reply(self, timeout=timedelta(seconds=30)) -> None:
        """Wait and periodically check if there is message in the queue, once there is, quit."""
        start_time = datetime.now()
        with self.connection() as connection:
            channel = connection.channel()
            self._create_queue(channel)

            is_info = True  # log the first message as info and then debug to reduce clutter
            while datetime.now() - start_time < timeout:
                getattr(self.log, "info" if is_info else "debug")(
                    f"Waiting for message, exchange={self.input_exchange}, "
                    f"queue={self.queue_name}, "
                    f"remaining={timeout - (datetime.now() - start_time)}"
                )
                is_info = False
                if not self._is_queue_empty(channel):
                    method, properties, body = channel.basic_get(self.queue_name)
                    self.log.debug(f"Received message.")
                    try:
                        self.result = self._validate_body(body)
                        self.log.info(f"Computation done, average RGB: {self.result}")
                    except Exception as e:
                        self.log.error("Received message is not valid.", exc_info=e)
                        self.error = str(e)
                    finally:
                        self.running_thread = None
                        return
                time.sleep(1)

            self.log.error("Timed-out while waiting for the processed image.")
            self.error = "Wait timed out."
            self.running_thread = None

    def spawn_listener(self) -> None:
        def target():
            try:
                self.wait_for_reply()
            except Exception as e:
                self.log.error("Wait thread failed.", exc_info=e)

        self.running_thread = threading.Thread(target=target)
        self.running_thread.start()

    def send(self) -> None:
        """Send image data to the system for processing."""
        with self.connection() as conn:
            channel = conn.channel()
            channel.exchange_declare(exchange=self.output_exchange, exchange_type='direct')
            channel.basic_publish(
                exchange=self.output_exchange,
                routing_key=self.output_routing_key,
                body=json.dumps({
                    'id': self.image_id,
                    'image': base64.b64encode(self.image_bytes).decode(),
                }).encode(),
            )
            self.log.debug(f"Sending image size={self.data_size_kb}kB")
            self.log.info(f"Sent, exchange={self.output_exchange}, key={self.output_routing_key}")
