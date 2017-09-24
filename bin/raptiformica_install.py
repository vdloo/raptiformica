#!/usr/bin/env python3
from raptiformica.cli import install

if __name__ == '__main__':
    install()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
