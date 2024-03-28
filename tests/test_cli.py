from ids_validator.cli import ids_validator_cli

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

def test_cli():
    ...