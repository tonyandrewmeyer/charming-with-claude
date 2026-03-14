"""Logging and crash reporting setup.

Configures:
- File logging (debug level) to .crash.log in the project root
- Plain tracebacks on stderr (no fancy formatting)
- sys.excepthook that writes full crash context to .crash.log
"""

from __future__ import annotations

import logging
import platform
import sys
import traceback
from datetime import datetime, timezone

from review_tool.config import PROJECT_ROOT

CRASH_LOG = PROJECT_ROOT / ".crash.log"
MAX_CRASH_LOG_SIZE = 1_000_000  # ~1MB, rotate by truncating old content


def setup_logging() -> None:
    """Configure logging and install the crash handler."""
    _configure_file_logging()
    _install_crash_handler()


def _configure_file_logging() -> None:
    """Set up rotating file handler for debug-level logging."""
    # Truncate if it's gotten too large
    if CRASH_LOG.exists() and CRASH_LOG.stat().st_size > MAX_CRASH_LOG_SIZE:
        lines = CRASH_LOG.read_text().splitlines()
        # Keep the last ~half
        CRASH_LOG.write_text("\n".join(lines[len(lines) // 2 :]) + "\n")

    handler = logging.FileHandler(CRASH_LOG, mode="a")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)

    # Keep stderr output at WARNING to avoid noise
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(stderr_handler)

    logging.info(
        "review-tool starting — Python %s on %s", sys.version, platform.system()
    )


def _install_crash_handler() -> None:
    """Replace sys.excepthook with one that writes to .crash.log."""
    _original_hook = sys.excepthook

    def _crash_hook(exc_type, exc_value, exc_tb):
        """Write a detailed crash report, then print a short message."""
        # Write detailed report to file
        try:
            with open(CRASH_LOG, "a") as f:
                f.write("\n" + "=" * 72 + "\n")
                f.write(f"CRASH at {datetime.now(timezone.utc).isoformat()}\n")
                f.write(f"Python: {sys.version}\n")
                f.write(f"Platform: {platform.platform()}\n")
                f.write(f"Args: {sys.argv}\n")
                f.write("-" * 72 + "\n")
                traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
                f.write("=" * 72 + "\n")
        except Exception:
            pass  # Can't do much if logging itself fails

        # Print plain, short traceback to stderr
        traceback.print_exception(exc_type, exc_value, exc_tb)
        print(f"\nCrash details written to {CRASH_LOG}", file=sys.stderr)

    sys.excepthook = _crash_hook
