import logging  # isort: skip

from ids_validator.setup_logging import connect_formatter

logger = logging.getLogger(__name__)
connect_formatter(logger)
