# This file is part of IMASPy.
# You should have received the IMASPy LICENSE file with this project.

from . import _version

__version__ = _version.get_versions()["version"]

version = __version__
