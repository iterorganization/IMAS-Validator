import difflib
import logging
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)


class InvalidRulesetPath(FileNotFoundError):
    """Error when the ruleset path is not found"""

    def __init__(self, path: Path) -> None:
        super().__init__(f"Ruleset path {str(path)!r} cannot be found.")


class InvalidRulesetName(ValueError):
    """Error when the ruleset name is not found"""

    def __init__(self, name: str, available: List[Path]) -> None:
        available_list = [p.name for p in available]
        close_matches = difflib.get_close_matches(name, available_list, n=1)
        if close_matches:
            suggestions = f"Did you mean {close_matches[0]!r}?"
        else:
            suggestions = f"Available versions are {', '.join(sorted(available_list))}"
        super().__init__(f"Ruleset name {name!r} cannot be found. {suggestions}")


class EmptyRuleFileWarning(Warning):
    """Warning when a file contains no rules"""

    def __init__(self, file: Path) -> None:
        super().__init__(f"Ruleset file {str(file)!r} does not contain any rules")


class WrongFileExtensionError(ValueError):
    """Error when a ruleset file does not have .py as a file extension"""

    def __init__(self, file: Path) -> None:
        super().__init__(f"Ruleset file {str(file)!r} is not a python file")
