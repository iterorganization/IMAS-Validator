import logging  # isort: skip
from pathlib import Path

from ids_validator.setup_logging import connect_formatter

from ._version import version  # noqa: F401
from ._version import version_tuple  # noqa: F401

__version__ = version
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
connect_formatter(logger)


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent
