import os

import pytest


TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data")


@pytest.fixture(scope="session")
def test_data_dir():
    return TEST_DIR


@pytest.fixture(params=["#000000.jpg", "#c0c0c0.jpg"])
def image(request, test_data_dir):
    """Read test images as bytes."""
    expected_avg, _ = request.param.split(".")
    with open(os.path.join(test_data_dir, request.param), "rb") as img:
        image_bytes = img.read()
    return image_bytes, expected_avg
