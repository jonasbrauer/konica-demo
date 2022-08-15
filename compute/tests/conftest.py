import pytest


@pytest.fixture(params=["#000000.jpg", "#c0c0c0.jpg"])
def image(request):
    """Read test images as bytes."""
    expected_avg, _ = request.param.split(".")
    with open(f"./test_data/{request.param}", "rb") as img:
        image_bytes = img.read()
    return image_bytes, expected_avg
