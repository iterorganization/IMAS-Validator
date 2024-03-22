"""Create a default log handler for ids_validator
"""

import logging


class _PrettyFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    light_grey = "\x1b[90m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    formatstr = (
        "%(asctime)s %(levelname)-8s %(message)s "
        f"{light_grey}@%(filename)s:%(lineno)d{reset}"
    )
    time_format = "%H:%M:%S"

    FORMATS = {
        logging.DEBUG: logging.Formatter(light_grey + formatstr, time_format),
        logging.INFO: logging.Formatter(formatstr, time_format),
        logging.WARNING: logging.Formatter(yellow + formatstr, time_format),
        logging.ERROR: logging.Formatter(red + formatstr, time_format),
        logging.CRITICAL: logging.Formatter(bold_red + formatstr, time_format),
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        return formatter.format(record)


def default_stream_handler() -> logging.StreamHandler:
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(_PrettyFormatter())
    return ch


def connect_formatter(logger: logging.Logger) -> None:
    """Connect general formatter to given logger"""
    logger.addHandler(default_stream_handler())
