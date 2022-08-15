import json
import os
from contextlib import contextmanager

import pika

from app import get_logger
from app.image import Image


log = get_logger(__name__)


class Compute:

    def __init__(self) -> None:
        self.queue_name = None  # dynamic queue, created & bound on start-up

        self.scan_dirs = os.environ.get("SCAN_DIRS")
        self.broker_host = os.environ.get("BROKER_HOST")
        self.broker_port = os.environ.get("BROKER_PORT") or 5672
        self.input_exchange = os.environ.get("INPUT_EXCHANGE")
        self.input_routing_key = os.environ.get("INPUT_ROUTING_KEY") or "compute"
        self.output_exchange = os.environ.get('OUTPUT_EXCHANGE')
        self.output_routing_key = os.environ.get('OUTPUT_ROUTING_KEY') or "computed"

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
            log.error('Unexpected error.', exc_info=e)
        finally:
            connection.close()

    def compute_callback(self, channel, method, properties, body):
        """Compute the average color and forward to the 'computed' exchange."""
        body = json.loads(body)
        image_uuid = body['id']

        # get a new logger for each 'compute task'
        logger = get_logger(image_uuid)
        image = Image.from_b64(body['image'])
        logger.info("Received image")
        # image_bytes = base64.b64decode(image_data.encode())
        # with open(f"/var/image_data/{image_uuid}.jpg", 'wb+') as new_image:
        #     new_image.write(image.image_data)
        # logger.info(f"Written: {f'/var/image_data/{image_uuid}.jpg'}")

        logger.info(f"Processing image {len(image.image_data) / 1000} kB")
        computed_average_color = image.get_average_rgb()
        logger.info(f"Image processed, result:  {computed_average_color}")

        routing_key = ".".join([image_uuid, self.output_routing_key])
        channel.basic_publish(
            exchange=self.output_exchange,
            routing_key=routing_key,
            body=json.dumps({
                'id': image_uuid,
                'image': image.to_b64_string(),
                'rgb': computed_average_color
            }).encode()
        )
        logger.info(
            f"Message sent, exchange={self.output_exchange}, "
            f"key={self.output_routing_key}"
        )

    def start_listening(self):
        with self.connection() as conn:
            # 1) set up exchanges/queues
            channel = conn.channel()
            channel.exchange_declare(exchange=self.input_exchange, exchange_type='direct')
            result = channel.queue_declare(queue="", exclusive=True)
            self.queue_name = result.method.queue
            channel.queue_bind(
                exchange=self.input_exchange,
                queue=self.queue_name,
                routing_key=self.input_routing_key
            )
            channel.exchange_declare(exchange=self.output_exchange, exchange_type='topic')

            def callback(ch, method, properties, body):
                return self.compute_callback(ch, method, properties, body)

            # 2) start listening
            log.info("Waiting for images to be processed... To exit press CTRL+C")
            log.debug(
                f"Consuming: exchange={self.input_exchange}, "
                f"key={self.input_routing_key}, "
                f"queue={self.queue_name}."
            )
            channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            channel.start_consuming()
