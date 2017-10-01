#!/usr/bin/env python3
from raptiformica.cli import advertise

if __name__ == '__main__':
    advertise()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
