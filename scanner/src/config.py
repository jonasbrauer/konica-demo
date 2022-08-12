
class Config(object):
    LOG_FILE = '/var/log/generator.log'
    # LOG_FILE = None

    BROKER_HOST = 'rabbitmq'
    BROKER_PORT = 5672
    COMPUTE_QUEUE = 'to_be_processed'

    SCAN_DIRS = ['/var/']
