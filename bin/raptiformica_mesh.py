#!/usr/bin/env python3
from raptiformica.cli import mesh

if __name__ == '__main__':
    mesh()
else:
    raise RuntimeError("This script is an entry point and can not be imported")
