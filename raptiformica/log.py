import logging
import sys

def setup_logging(level=logging.INFO):
    logger = logging.getLogger('raptiformica')
    logger.setLevel(level)
    consule_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    return logger
