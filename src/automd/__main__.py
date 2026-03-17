#!/usr/bin/env python3
"""
AutoMD package entry point for python -m automd
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
