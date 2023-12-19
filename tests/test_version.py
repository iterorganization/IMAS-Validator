from packaging.version import Version

import ids_validator


def test_version():
    version = ids_validator.__version__
    assert version != ""
    assert isinstance(version, str)
    # Check that the version can be parsed by packaging.version.Version
    Version(version)
