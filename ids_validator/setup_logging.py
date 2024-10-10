"""Create a default log handler for ids_validator
"""

import logging

import imaspy  # noqa: F401, imported to overwrite logging handlers at correct timing
from rich.logging import RichHandler


class _PrettyFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    light_grey = "[light grey]"
    yellow = "[yellow]"
    red = "[red]"
    bold_red = "[bold red]"
    reset = "[/]"

    formatstr = (
        "%(asctime)s %(levelname)-8s %(message)s "
        f"{light_grey}@%(filename)s:%(lineno)d{reset}"
    )
    time_format = "%H:%M:%S"

    FORMATS = {
        logging.DEBUG: logging.Formatter(light_grey + formatstr, time_format),
        logging.INFO: logging.Formatter("[white]" + formatstr, time_format),
        logging.WARNING: logging.Formatter(yellow + formatstr, time_format),
        logging.ERROR: logging.Formatter(red + formatstr, time_format),
        logging.CRITICAL: logging.Formatter(bold_red + formatstr, time_format),
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        return formatter.format(record)


def default_stream_handler() -> RichHandler:
    ch = RichHandler(markup=True, show_time=False, show_path=False, show_level=False)
    ch.setFormatter(_PrettyFormatter())
    return ch


def connect_formatter(logger: logging.Logger) -> None:
    """Connect general formatter to given logger"""
    logger.addHandler(default_stream_handler())
    setup_rich_log_handler(False)


def setup_rich_log_handler(quiet: bool) -> None:
    """Setup rich.logging.RichHandler on the root logger.

    Args:
        quiet: When True: set log level of the `imaspy` logger to WARNING or higher.
    """
    # Disable default imaspy log handler
    imaspy_logger = logging.getLogger("imaspy")
    for handler in imaspy_logger.handlers:
        imaspy_logger.removeHandler(handler)
    if quiet:  # Silence IMASPy INFO messages
        # If loglevel is less than WARNING, set it to WARNING:
        imaspy_logger.setLevel(max(logging.WARNING, imaspy_logger.getEffectiveLevel()))
