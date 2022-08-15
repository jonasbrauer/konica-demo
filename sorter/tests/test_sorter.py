import base64
import json
import os
import random

import mock
import pytest

from app.sorter import Sorter, SorterError


TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data")


@pytest.fixture(autouse=True)
def target_dir(monkeypatch):
    random_dir = f"/tmp/random-dir-{random.randint(1, 1000)}"
    monkeypatch.setenv("TARGET_DIR", random_dir)
    return random_dir


@pytest.fixture
def image():
    """Read test images as bytes."""
    with open(f"{TEST_DIR}/#c0c0c0.jpg", "rb") as img:
        image_bytes = img.read()
    return image_bytes, "#c0c0c0"


@pytest.fixture
def image_asb64(image):
    image_bytes, _ = image
    return base64.b64encode(image_bytes).decode()


@pytest.fixture
def invalid_image():
    """Read test images as bytes."""
    with open(f"{TEST_DIR}/invalid.jpg", "rb") as img:
        image_bytes = img.read()
    return image_bytes


def test_setup_target_dir():
    assert not os.path.isdir(os.environ.get("TARGET_DIR"))
    sorter = Sorter()
    assert os.path.isdir(sorter.target_dir)


@pytest.mark.parametrize("body", [
    {"id": "uuid-123", "image": "base64image", "rgb": "#ffffff"},
])
def test_validate_body(body):
    assert Sorter._validate_body(json.dumps(body)) == body


@pytest.mark.parametrize("body", [
    {"id": None, "image": "base64image", "rgb": "#ffffff"},
    {"image": "base64image", "rgb": "#ffffff"},
    {"id": "uuid-123", "image": None, "rgb": "#ffffff"},
    {"id": "uuid-123", "rgb": "#ffffff"},
    {"id": "uudi-123", "image": "base64image", "rgb": None},
    {"id": "uudi-123", "image": "base64image"},
])
def test_validate_body_negative(body):
    with pytest.raises(SorterError):
        Sorter._validate_body(json.dumps(body))


def test_validate_image(image_asb64):
    assert Sorter._validate_image(image_data_b64_string=image_asb64)


def test_validate_image_negative(invalid_image):
    image_b64 = base64.b64encode(invalid_image).decode()
    with pytest.raises(SorterError):
        Sorter._validate_image(image_b64)


@mock.patch.object(Sorter, "connection")
def test_sort(mock_conn, image_asb64, target_dir):
    computed_avg_rgb = "#ffffff"
    image_id = f"image-{random.randint(1000, 9999)}"
    expected_image_file_name = f"{image_id}.JPEG"

    sorter = Sorter()
    body = json.dumps({
        "id": image_id,
        "rgb": computed_avg_rgb,
        "image": image_asb64
    })
    sorter.sort_callback(body)
    assert os.path.isfile(os.path.join(target_dir, computed_avg_rgb, expected_image_file_name))
