#! /usr/bin/env python3
"""
Compute component of the sorting system
* Waits for an image file to appear in the queue
* Computes the average RGB
* Sends back both the image and the RGB

Modify behavior using these environment variables:
* LOG_LEVEL
* LOG_FILE
* BROKER_HOST
* BROKER_PORT (defaults to 5672)
* INPUT_EXCHANGE: where to listen for incoming compute tasks
* INPUT_ROUTING_KEY (defaults to 'compute')
* OUTPUT_EXCHANGE: where to send the computation results
* OUTPUT_ROUTING_KEY: (defaults to 'computed')

"""
import random
import time

from app import get_logger
from app.compute import Compute

log = get_logger('MAIN')


def compute_average_color(image_data):
    log.debug(f"Processing image: {image_data}")
    time.sleep(3)
    colors = ['#2b2b2b', "#9e2927", "#549453", "#ffffff", "#0994c4"]
    random.shuffle(colors)
    log.debug(f"Image processed, average color: {colors[0]}")
    return colors[0]


def main():
    log.info("===============")
    log.info("COMPUTE STARTED")
    log.info("===============\n")

    compute = Compute()
    compute.start_listening()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log.error("Unexpected error", exc_info=e)
            time.sleep(5)
