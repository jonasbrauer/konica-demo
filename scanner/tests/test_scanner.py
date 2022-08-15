import json
import os
import threading

import mock
import pytest

from app.scanner import Scanner

TEST_DATA_PATH = "./test_data"


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    """Set-up test environment variables."""
    monkeypatch.setenv("WATCH_DIR", TEST_DATA_PATH)
    monkeypatch.setenv("SCAN_INTERVAL_SECS", "1")


@pytest.fixture
def test_dir():
    """List test directory and return files only."""
    listing = os.listdir(TEST_DATA_PATH)
    return [
        item for item in listing if os.path.isfile(os.path.join(TEST_DATA_PATH, item))
    ]


def test_scan_test_dir(test_dir):
    scanner = Scanner()
    files = scanner.scan(TEST_DATA_PATH)
    assert len(files) == len(test_dir)
    assert files == {
        os.path.join(TEST_DATA_PATH, file) for file in test_dir
    }


@mock.patch.object(Scanner, "connection")
def test_scanner(mock_connection, test_dir):
    """Test that scanner scans requested directory properly."""
    scanner = Scanner()
    scanner.publish_image = mock.MagicMock()
    thread = threading.Thread(target=scanner.start_scanning, daemon=False)

    scanner.exit_event.set()
    thread.start()
    thread.join()

    assert scanner.publish_image.call_count == len(test_dir)
    scanner.publish_image.assert_called_with(
        os.path.join(TEST_DATA_PATH, test_dir[-1])
    )


def test_scanner_publish(test_dir):
    """Test that scanner publishes valid message containing image ID and image data."""

    def assert_publish(exchange=None, routing_key=None, body=None):
        body = json.loads(body)
        assert body.get("id"), "image ID missing"
        assert body.get("image"), "image data missing"
        # todo: assert that the image data is valid

    scanner = Scanner()
    with mock.patch.object(scanner, "connection"):
        with scanner.connection() as conn:
            conn.channel().basic_publish.side_effect = assert_publish
        thread = threading.Thread(target=scanner.start_scanning, daemon=False)
        scanner.exit_event.set()
        thread.start()
        thread.join()
        with scanner.connection() as conn:
            assert conn.channel().basic_publish.call_count == len(test_dir)
