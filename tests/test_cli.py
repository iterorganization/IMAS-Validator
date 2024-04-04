from ids_validator.cli import ids_validator_cli
from ids_validator.cli.commands import validate_command
import imas
import imaspy
import pytest
import argparse

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
    
    assert str(command_object) ==\
           "VALIDATE URI=i VALIDATE_OPTIONS=ValidateOptions(rulesets=['test_ruleset']," \
           " use_bundled_rulesets=True," \
           " extra_rule_dirs=[PosixPath('.')]," \
           " apply_generic=True," \
           " use_pdb=False," \
           " rule_filter=RuleFilter(name=[], ids=[]))"


