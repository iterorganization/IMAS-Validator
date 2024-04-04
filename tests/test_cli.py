from ids_validator.cli import ids_validator_cli
from ids_validator.cli.commands import validate_command
import imas
import imaspy
import pytest
import argparse
from pathlib import Path

def test_cli_no_arguments():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        ids_validator_cli.main([])

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0

def test_cli_wrong_command():
    argv = ['wrong_command']

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        ids_validator_cli.main(argv)

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2

def test_non_existing_pulsefile(tmp_path):
    empty_db_dir = tmp_path / "empty_testdb"
    empty_db_dir.mkdir()

    argv = ['validate', f'imas:hdf5?path={empty_db_dir}']

    with pytest.raises(imaspy.exception.LowlevelError) as pytest_wrapped_e:
        ids_validator_cli.main(argv)

def test_existing_pulsefile(tmp_path):
    db_dir = tmp_path / "testdb"
    db_dir.mkdir()

    uri = f"imas:hdf5?path={db_dir}"
    entry = imas.DBEntry(uri=uri, mode="x")
    entry.close()

    argv = ['validate', uri]

    ids_validator_cli.main(argv)

def test_validate_command_str_cast():
    args = argparse.Namespace(command='Validate',
                              uri="imas:hdf5?path=testdb",
                              ruleset=[["test_ruleset"]],
                              extra_rule_dirs=[[""]],
                              no_generic=True,
                              debug=False)

    command_object = validate_command.ValidateCommand(args)

    assert command_object.validate_options.rulesets == ['test_ruleset']
    assert command_object.validate_options.use_bundled_rulesets == True
    assert command_object.validate_options.extra_rule_dirs == [Path('.')]
    assert command_object.validate_options.apply_generic == True
    assert command_object.validate_options.use_pdb == False
    assert command_object.validate_options.rule_filter.name == []
    assert command_object.validate_options.rule_filter.ids == []
