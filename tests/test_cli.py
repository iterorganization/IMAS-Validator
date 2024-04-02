from ids_validator.cli import ids_validator_cli
from pathlib import Path
import imas
import imaspy
import shutil
import pytest
import os

def test_cli_no_arguments():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        ids_validator_cli.main([])

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 42

def test_cli_wrong_command():
    argv = ['wrong_command']

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        ids_validator_cli.main(argv)

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 42

def test_non_existing_pulsefile():

    tmp_dir = Path(".") / "empty_testdb"
    tmp_dir.mkdir()

    argv = ['validate', 'imas:hdf5?path=empty_testdb']

    with pytest.raises(imaspy.exception.LowlevelError) as pytest_wrapped_e:
        ids_validator_cli.main(argv)

def test_existing_pulsefile():

    tmp_dir = Path(".") / "testdb"
    tmp_dir.mkdir()

    entry = imas.DBEntry("imas:hdf5?path=testdb", mode="x")
    entry.close()

    argv = ['validate', 'imas:hdf5?path=testdb']

    ids_validator_cli.main(argv)
