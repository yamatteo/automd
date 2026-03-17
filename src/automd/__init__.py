#!/usr/bin/env python3
"""
AutoMD - Automatic project documentation via MCP protocol
"""

import asyncio
import sys
from pathlib import Path

from .server import main as server_main


def main() -> None:
    """Main entry point for AutoMD MCP server"""
    try:
        asyncio.run(server_main())
    except KeyboardInterrupt:
        print("\nAutoMD server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"AutoMD server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
