#!/usr/bin/env python3
from raptiformica.cli import agent

if __name__ == '__main__':
    agent()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
