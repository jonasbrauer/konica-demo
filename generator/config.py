
class Config(object):
    BROKER_HOST = 'rabbitmq'
    BROKER_PORT = 5672

    COMPUTE_QUEUE = 'to_be_processed'

    LOG_FILE = '/var/log/generator.log'
