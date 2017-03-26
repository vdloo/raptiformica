#!/usr/bin/env python3
from raptiformica.cli import join

if __name__ == '__main__':
    join()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
