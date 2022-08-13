import pytest
from app.scanner import Scanner


class TestConfig:
    LOG_FILE = None

    BROKER_HOST = 'rabbitmq'
    BROKER_PORT = 5672
    COMPUTE_QUEUE = 'to_be_processed'

    SCAN_DIRS = ['/var/']


@pytest.fixture
def scanner():
    scanner = Scanner(config=TestConfig)
    return scanner


def test_start_scan(scanner):
    pass
