#! /usr/bin/env python3
"""
Generator component of the sorting system
* Scans a given directory for file changes
* On a 'change detected' reads the image and sends it to the broker
"""
import logging

from config import Config
from scanner import Scanner

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
handler = logging.FileHandler('/var/log/main.log', mode="w")
log.addHandler(handler)


if __name__ == "__main__":
    try:
        scanner = Scanner(config=Config)
        scanner.start_scanning()
    except Exception as e:
        log.error("main failed", exc_info=e)
        raise
