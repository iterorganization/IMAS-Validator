import difflib
import logging
from pathlib import Path
from typing import List, Optional

from packaging.version import Version

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
            suggestions = f"Available rulesets are {', '.join(sorted(available_list))}"
        super().__init__(f"Ruleset name {name!r} cannot be found. {suggestions}")


class EmptyRuleFileWarning(Warning):
    """Warning when a file contains no rules"""

    def __init__(self, file: Path) -> None:
        super().__init__(f"Ruleset file {str(file)!r} does not contain any rules")


class WrongFileExtensionError(ValueError):
    """Error when a ruleset file does not have .py as a file extension"""

    def __init__(self, file: Path) -> None:
        super().__init__(f"Ruleset file {str(file)!r} is not a python file")


class IMASVersionError(RuntimeError):
    """Error raised when IMAS is not available, or of the wrong version."""

    def __init__(self, version_found: Optional[Version] = None) -> None:
        if version_found is None:
            version_msg = "No IMAS install could be found."
        else:
            version_msg = f"Found IMAS install with version {version_found}."

        super().__init__(
            "IDS Validation requires an IMAS installation of version 5.1 or newer."
            f" {version_msg}. See the README for more details."
        )


class ValidateDebugException(RuntimeError):
    """Error raised specifically to open the debugger for failed validation tests"""

    def __init__(self) -> None:
        super().__init__("Go to debugger")
