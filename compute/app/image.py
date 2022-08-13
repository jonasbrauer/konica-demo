import base64
import io
import random

from PIL import Image as PImage
from numpy import asarray, mean

from app import get_logger

log = get_logger(__name__)


class Image:

    def __init__(self, image_data: bytes) -> None:
        self.image_data = image_data

    @staticmethod
    def rgb_to_hex(rgb: list) -> str:
        if len(rgb) != 3:
            raise ValueError(f"Invalid RGB input: {rgb}, expected 3 items")
        try:
            rgb = [round(item) for item in rgb]
        except ValueError as e:
            raise ValueError(f"Invalid RGB input: {rgb}", e)

        return '#' + ''.join([
            '{:02x}'.format(item) if item < 255 else 255 for item in rgb
        ])

    @classmethod
    def from_b64(cls, b64_string: str):
        image_bytes = base64.b64decode(b64_string.encode())
        return cls(image_bytes)

    def to_b64_string(self) -> str:
        return base64.b64encode(self.image_data).decode()

    def get_average_rgb(self):
        stream = io.BytesIO(self.image_data)
        image = PImage.open(stream)
        log.debug(f"'{image.format}' image loaded: {image.height}x{image.width}")

        result = mean(asarray(image), axis=(0, 1))
        result_hex = self.rgb_to_hex(list(result))
        log.debug(f"Image processed, result mean: RGB{result}, HEX[{result_hex}]")

        return result_hex
