import base64
import io

from PIL import Image as PImage, UnidentifiedImageError
from numpy import asarray, mean

from app import get_logger

log = get_logger(__name__)


class ImageError(Exception):
    pass


class Image:

    def __init__(self, image_data: bytes) -> None:
        self.image_data = image_data

    @staticmethod
    def rgb_to_hex(rgb: list) -> str:
        def parse_number(item):
            number = round(float(item))
            if number < 0:
                return 0
            if number > 255:
                return 255
            return number

        try:
            if len(rgb) != 3:
                raise ImageError(f"Invalid RGB input: {rgb}, expected 3 items")
            rgb = [parse_number(item) for item in rgb]
        except (ValueError, TypeError) as e:
            raise ImageError(f"Invalid RGB input: {rgb}", e)

        return '#' + ''.join(['{:02x}'.format(item) for item in rgb])

    @classmethod
    def from_b64(cls, b64_string: str):
        image_bytes = base64.b64decode(b64_string.encode())
        return cls(image_bytes)

    def to_b64_string(self) -> str:
        return base64.b64encode(self.image_data).decode()

    def get_average_rgb(self):
        stream = io.BytesIO(self.image_data)
        try:
            image = PImage.open(stream)
        except UnidentifiedImageError as e:
            raise ImageError("Invalid image data", e)

        log.debug(f"'{image.format}' image loaded: {image.height}x{image.width}")

        result = mean(asarray(image), axis=(0, 1))
        result_hex = self.rgb_to_hex(list(result))
        log.debug(f"Image processed, result mean: RGB{result}, HEX[{result_hex}]")

        return result_hex
