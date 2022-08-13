import base64
import json

import mock

from app.compute import Compute


def test_compute_callback(image):
    image_bytes, expected_hex = image
    compute = Compute()

    test_body = json.dumps({
        'id': '1234',
        'image': base64.b64encode(image_bytes).decode()
    })

    def assert_body(exchange=None, routing_key=None, body=None):
        sent_body = json.loads(body)
        assert sent_body.get("id"), "image id missing"
        assert sent_body.get("image"), "image data missing"
        assert sent_body.get("rgb") == expected_hex

    mocked_channel = mock.MagicMock()
    mocked_channel.basic_publish = mock.Mock(side_effect=assert_body)
    compute.compute_callback(
        channel=mocked_channel,
        method=None,
        properties=None,
        body=test_body
    )
    mocked_channel.basic_publish.assert_called_once()
