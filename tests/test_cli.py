from ids_validator.cli import ids_validator_cli
import imas
import imaspy
import shutil
import pytest

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
    # Make sure that testdb doesn't exist
    shutil.rmtree("testdb",ignore_errors=True)

    argv = ['validate', 'imas:mdsplus?path=testdb']

    with pytest.raises(imaspy.exception.LowlevelError) as pytest_wrapped_e:
        ids_validator_cli.main(argv)

def test_existing_pulsefile():

    entry = imas.DBEntry("imas:mdsplus?path=testdb", mode="x")
    entry.close()

    argv = ['validate', 'imas:mdsplus?path=testdb']

    ids_validator_cli.main(argv)
