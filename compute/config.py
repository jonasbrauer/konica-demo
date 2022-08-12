
class Config(object):
    BROKER_HOST = 'rabbitmq'
    BROKER_PORT = 5672

    INPUT_QUEUE = 'to_be_processed'
    OUTPUT_QUEUE = 'to_be_sorted'

    LOG_FILE = '/var/log/compute.log'
