import os
import uuid


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def generate_uuid():
    return str(uuid.uuid4())
