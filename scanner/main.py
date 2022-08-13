#! /usr/bin/env python3
"""
Generator component of the sorting system
* Scans a given directory for file changes
* On a 'change detected' reads the image and sends it to the broker

Modify behavior using these environment variables:
* LOG_LEVEL
* LOG_FILE
* LOG_LEVEL
* LOG_LEVEL

"""
import logging

from app.scanner import Scanner

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
handler = logging.FileHandler('/var/log/main.log', mode="w")
log.addHandler(handler)


if __name__ == "__main__":
    try:
        scanner = Scanner()
        scanner.start_scanning()
    except Exception as e:
        log.error("main failed", exc_info=e)
        raise
