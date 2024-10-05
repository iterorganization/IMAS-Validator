import logging  # isort: skip
from pathlib import Path

from ids_validator.setup_logging import connect_formatter

from . import _version

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
connect_formatter(logger)

__version__ = _version.get_versions()["version"]

version = __version__


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent
