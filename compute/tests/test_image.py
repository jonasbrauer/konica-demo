import os

import pytest

from app.image import Image, ImageError


@pytest.mark.parametrize('rgb,expected', [
    ([86, 84, 86], "#565456"),
    ([94, 153, 256], "#5e99ff"),
    ([159, 201, 126], "#9fc97e"),
    (["159", "201", "126"], "#9fc97e"),
    ([158.89, 201., 126.49], "#9fc97e"),
    ([158.89, 201., 126.49, 255], "#9fc97eff"),
])
def test_rgb_to_hex(rgb, expected):
    assert Image.rgb_to_hex(rgb) == expected


@pytest.mark.parametrize('rgb', [
    "just a string",
    [158, 84, "string"],
])
def test_rgb_to_hex_invalid(rgb):
    with pytest.raises(ImageError):
        Image.rgb_to_hex(rgb)


@pytest.fixture
def invalid_image(test_data_dir):
    with open(os.path.join(test_data_dir, "invalid.jpg"), "rb") as img:
        image_bytes = img.read()
    return image_bytes


def test_average_calculation(image):
    image_bytes, expected_avg = image
    test_image = Image(image_bytes)
    assert test_image.get_average_rgb() == expected_avg


def test_invalid_image(invalid_image):
    test_image = Image(invalid_image)
    with pytest.raises(ImageError):
        test_image.get_average_rgb()
