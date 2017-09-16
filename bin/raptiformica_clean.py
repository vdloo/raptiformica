#!/usr/bin/env python3
from raptiformica.cli import clean

if __name__ == '__main__':
    clean()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
