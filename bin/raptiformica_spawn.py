#!/usr/bin/env python3
from raptiformica.cli import spawn

if __name__ == '__main__':
    spawn()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
