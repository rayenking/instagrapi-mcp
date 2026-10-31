"""Entry point: register tools and run the FastMCP server over stdio."""

import logging
import sys

from . import mcp
from . import tools as _tools  # noqa: F401  (import registers every @mcp.tool)


def _configure_logging() -> None:
    """Keep every log line off stdout - the stdio transport owns it."""
    ig_logger = logging.getLogger("instagrapi")
    ig_logger.propagate = False
    if not ig_logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.WARNING)
        ig_logger.addHandler(handler)


def main() -> None:
    _configure_logging()
    mcp.run()  # stdio


if __name__ == "__main__":
    main()
