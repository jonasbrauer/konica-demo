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
import time

from app import get_logger
from app.compute import Compute

log = get_logger('MAIN')


def main():
    log.info("""
░▒█▀▀▄░▒█▀▀▀█░▒█▀▄▀█░▒█▀▀█░▒█░▒█░▀▀█▀▀░▒█▀▀▀
░▒█░░░░▒█░░▒█░▒█▒█▒█░▒█▄▄█░▒█░▒█░░▒█░░░▒█▀▀▀
░▒█▄▄▀░▒█▄▄▄█░▒█░░▒█░▒█░░░░░▀▄▄▀░░▒█░░░▒█▄▄▄""")
    while True:
        try:
            compute = Compute()
            compute.start_listening()
        except Exception as e:
            log.error("Unexpected error", exc_info=e)
            time.sleep(10)


if __name__ == "__main__":
    main()
