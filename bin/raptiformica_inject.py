#!/usr/bin/env python3
from raptiformica.cli import inject

if __name__ == '__main__':
    inject()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
