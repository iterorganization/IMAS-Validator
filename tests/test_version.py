from packaging.version import Version

import imas_validator


def test_version():
    version = imas_validator.__version__
    assert version != ""
    assert isinstance(version, str)
    # Check that the version can be parsed by packaging.version.Version
    Version(version)
