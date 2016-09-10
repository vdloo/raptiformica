#!/usr/bin/env python3
from raptiformica.cli import modprobe

if __name__ == '__main__':
    modprobe()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
