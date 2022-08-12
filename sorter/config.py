
class Config(object):
    BROKER_URL = 'rabbitmq'
    SORT_QUEUE = 'to_be_sorted'

    SORT_ROOT_PATH = '/var/sort'

    LOG_FILE = '/var/log/sorter.log'
