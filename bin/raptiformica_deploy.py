#!/usr/bin/env python3
from raptiformica.cli import deploy

if __name__ == '__main__':
    deploy()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
