#! /usr/bin/env python3
"""
Sorting component of the sorting system
* Waits for an image with a computed average RGB
* Sorts (puts it in a named folder) image file based on the average RGB
"""
import time

from app import get_logger
from app.sorter import Sorter

log = get_logger("MAIN")


def main():
    log.info("""
░▒█▀▀▀█░▒█▀▀▀█░▒█▀▀▄░▀▀█▀▀░▒█▀▀▀░▒█▀▀▄
░░▀▀▀▄▄░▒█░░▒█░▒█▄▄▀░░▒█░░░▒█▀▀▀░▒█▄▄▀
░▒█▄▄▄█░▒█▄▄▄█░▒█░▒█░░▒█░░░▒█▄▄▄░▒█░▒█""")
    while True:
        try:
            sorter = Sorter()
            sorter.start_listening()
        except Exception as e:
            log.error("Unexpected error", exc_info=e)
            time.sleep(10)


if __name__ == "__main__":
    main()
