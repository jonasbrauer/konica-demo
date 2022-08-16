#! /usr/bin/env python3
"""
Generator component of the sorting system
* Scans a given directory for file changes
* On a 'change detected' reads the image and sends it to the broker

Modify behavior using these environment variables:
* LOG_LEVEL
* LOG_FILE
* WATCH_DIR: directory to be periodically scanned for new images
* SCAN_INTERVAL_SECS (defaults to 5)
* BROKER_HOST
* BROKER_PORT (defaults to 5672)
* OUTPUT_EXCHANGE: where to send the computation results
* OUTPUT_ROUTING_KEY: (defaults to 'compute')

"""
import time

from app import get_logger
from app.scanner import Scanner

log = get_logger("MAIN")


def main():
    log.info("""
░▒█▀▀▀█░▒█▀▀▄░█▀▀▄░▒█▄░▒█░▒█▄░▒█░▒█▀▀▀░▒█▀▀▄
░░▀▀▀▄▄░▒█░░░▒█▄▄█░▒█▒█▒█░▒█▒█▒█░▒█▀▀▀░▒█▄▄▀
░▒█▄▄▄█░▒█▄▄▀▒█░▒█░▒█░░▀█░▒█░░▀█░▒█▄▄▄░▒█░▒█""")
    while True:
        try:
            scanner = Scanner()
            scanner.start_scanning()
        except Exception as e:
            log.error("Unexpected error", exc_info=e)
            time.sleep(10)


if __name__ == "__main__":
    main()
