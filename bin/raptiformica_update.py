#!/usr/bin/env python3
from raptiformica.cli import update

if __name__ == '__main__':
    update()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
