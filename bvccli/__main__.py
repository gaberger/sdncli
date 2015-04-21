#!/usr/bin/env python
"""The main entry point. Invoke as `bvc' or `python -m bvc'.
"""
import sys
from .core import main


if __name__ == '__main__':
    sys.exit(main())