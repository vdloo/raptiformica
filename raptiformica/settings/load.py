from raptiformica.settings import BASE_CONFIG
from raptiformica.utils import load_json, write_json

from logging import getLogger

log = getLogger(__name__)


def load_config(config_file=BASE_CONFIG):
    """
    Load a config file or default to the base config
    :param str config_file: path to the .json config file
    :return dict: the config data
    """
    try:
        return load_json(config_file)
    except (OSError, ValueError):
        if config_file != BASE_CONFIG:
            log.warning("Failed loading config file {}. Falling back to base config {}".format(
                config_file, BASE_CONFIG
            ))
            config = load_config()
            write_config(config, config_file)
            return config
        else:
            log.error("No valid config available!")
            raise


def write_config(config, config_file):
    """
    Write the config to a config file
    :param dict config: The config to be dumped to json
    :param str config_file: The mutable config file
    :return None:
    """
    write_json(config, config_file)
