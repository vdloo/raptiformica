from os import path, makedirs, listdir
from uuid import uuid4
from json import dumps


def list_directories(directory):
    def is_directory(directory_item):
        return path.isdir(path.join(directory, directory_item))
    return filter(is_directory, listdir(directory))


def pretty_dump(data, empty_message='No data'):
    out = dumps(data, indent=2)
    return out if data else empty_message


def ensure_directory(directory):
    if not path.exists(directory):
        makedirs(directory)


def generate_uuid():
    return str(uuid4())
