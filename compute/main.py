#! /usr/bin/env python3
"""
Compute component of the sorting system
* Waits for a image file to appear in the queue
* Computes the average RGB
* Sends back both the image and the RGB
"""
import json
import logging
import time
import random

import pika

from config import Config

with open(Config.LOG_FILE, 'w'):
    pass  # clear the logfile on each restart
logging.basicConfig(filename=Config.LOG_FILE)
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


def compute_average_color(image_data):
    logger.debug(f"Processing image: {image_data}")
    time.sleep(10)
    colors = ['#2b2b2b', "#9e2927", "#549453", "#ffffff", "#0994c4"]
    random.shuffle(colors)
    logger.debug(f"Image processed, average color: {colors[0]}")
    return colors[0]


def main():
    logger.info("""
+--------------------+
|  STARTING COMPUTE  |
+--------------------+
""")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=Config.BROKER_HOST,
            port=Config.BROKER_PORT,
            connection_attempts=5,
            retry_delay=5,
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=Config.INPUT_QUEUE, durable=False)
    channel.queue_declare(queue=Config.OUTPUT_QUEUE, durable=False)

    def compute_callback(chan, method, properties, body):
        image_data = body
        computed_average_color = compute_average_color(image_data)

        response = {
            'color': computed_average_color,
        }

        chan.basic_publish(
            exchange="",
            routing_key=Config.OUTPUT_QUEUE,
            body=json.dumps(response)
        )

    channel.basic_consume(queue=Config.INPUT_QUEUE, on_message_callback=compute_callback)
    channel.start_consuming()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logger.error("Unexpected error", exc_info=e)
