import argparse
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import imas  # type: ignore
import numpy
import pytest

from imas_validator.cli import imas_validator_cli
from imas_validator.cli.commands import validate_command


def _run_cli_with_results(monkeypatch, output_path, validation_results):
    report_generator = Mock(txt="")
    summary_generator = Mock()
    junit_parser = Mock()
    junit_parser.html.return_value = ""

    monkeypatch.setattr(
        imas_validator_cli,
        "ValidationReportGenerator",
        lambda result: report_generator,
    )
    monkeypatch.setattr(
        imas_validator_cli,
        "SummaryReportGenerator",
        lambda results, today: summary_generator,
    )
    monkeypatch.setattr(imas_validator_cli, "Junit", lambda path: junit_parser)

    def execute(command):
        command._executed = True
        command._result = SimpleNamespace(
            imas_uri=command._uri,
            results=[SimpleNamespace(success=validation_results[command._uri])],
        )

    monkeypatch.setattr(validate_command.ValidateCommand, "execute", execute)
    argv = ["validate", *validation_results, "--output", str(output_path)]

    return imas_validator_cli.main(argv), report_generator, summary_generator


def _write_invalid_dataset(uri):
    ids = imas.IDSFactory().new("core_profiles")
    ids.ids_properties.homogeneous_time = 1
    ids.time = numpy.array([0.0])
    ids.profiles_1d.resize(1)
    profile = ids.profiles_1d[0]
    profile.grid.rho_tor_norm = numpy.linspace(0.0, 1.0, 4)
    profile.electrons.temperature = numpy.array([-1.0, 100.0, 50.0, 10.0])

    with imas.DBEntry(str(uri), "w") as entry:
        entry.put(ids)


def test_cli_no_arguments():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        imas_validator_cli.main([])

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_cli_wrong_command():
    argv = ["wrong_command"]

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        imas_validator_cli.main(argv)

    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2


def test_cli_returns_zero_when_all_datasets_pass(monkeypatch, tmp_path):
    exit_status, _, _ = _run_cli_with_results(monkeypatch, tmp_path, {"valid.nc": True})

    assert exit_status == 0


def test_cli_returns_one_when_any_dataset_fails(monkeypatch, tmp_path, capsys):
    exit_status, report_generator, summary_generator = _run_cli_with_results(
        monkeypatch,
        tmp_path,
        {"valid.nc": True, "invalid.nc": False},
    )

    assert exit_status == 1
    assert capsys.readouterr().out.splitlines()[-1] == "invalid.nc"
    assert report_generator.save_xml.call_count == 2
    assert report_generator.save_txt.call_count == 2
    summary_generator.save_html.assert_called_once()


def test_cli_entry_point_returns_one_and_writes_reports(tmp_path):
    uri = tmp_path / "invalid.nc"
    reports_path = tmp_path / "reports"
    _write_invalid_dataset(uri)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "imas_validator",
            "validate",
            str(uri),
            "--ruleset",
            "generic",
            "--output",
            str(reports_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert completed.stdout.splitlines()[-1] == str(uri)
    assert "FAILED validation." in completed.stdout
    assert len(list(reports_path.rglob("*.xml"))) == 1
    assert len(list(reports_path.rglob("*.txt"))) == 1
    assert len(list(reports_path.rglob("*.html"))) == 2


def test_cli_entry_point_preserves_argument_error_status():
    completed = subprocess.run(
        [sys.executable, "-m", "imas_validator", "validate"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2


@pytest.mark.skip(reason="Skipping this test due to imas-core unavailability")
def test_non_existing_pulsefile(tmp_path):
    empty_db_dir = tmp_path / "empty_testdb"
    empty_db_dir.mkdir()

    argv = ["validate", f"imas:hdf5?path={empty_db_dir}"]

    # When using imas_core >= 5.2, this raises an ALException. In earlier AL versions
    # IMAS-Python raises a LowlevelError.
    with pytest.raises(SystemExit):
        imas_validator_cli.main(argv)


@pytest.mark.skip(reason="Skipping this test due to imas-core unavailability")
def test_existing_pulsefile(tmp_path):
    db_dir = tmp_path / "testdb"
    db_dir.mkdir()

    uri = f"imas:hdf5?path={db_dir}"
    entry = imas.DBEntry(uri=uri, mode="x")
    entry.close()

    argv = ["validate", uri]

    imas_validator_cli.main(argv)


def test_non_existing_pulsefile(tmp_path):
    empty_db_dir = tmp_path / "empty_testdb"
    empty_db_dir.mkdir()

    argv = ["validate", f"{empty_db_dir}/pulse.nc"]

    # When using imas_core >= 5.2, this raises an ALException. In earlier AL versions
    # IMAS-Python raises a LowlevelError.
    with pytest.raises(Exception):
        imas_validator_cli.main(argv)


def test_existing_pulsefile(tmp_path):
    db_dir = tmp_path / "testdb"
    db_dir.mkdir()

    uri = f"{db_dir}/pulse.nc"
    entry = imas.DBEntry(uri=uri, mode="x")
    entry.close()

    argv = ["validate", uri]
    with pytest.raises(Exception):
        imas_validator_cli.main(argv)


def test_validate_command_str_cast():
    args = argparse.Namespace(
        command="Validate",
        uri="testdb/pulse.nc",
        ruleset=[["test_ruleset"]],
        extra_rule_dirs=[[""]],
        no_generic=True,
        debug=False,
        no_bundled=False,
        node_coverage=True,
        filter_name=[],
        filter_ids=[],
        filter=[["homogeneous_time", "core_profiles"]],
    )

    command_object = validate_command.ValidateCommand(args)

    assert command_object.validate_options.rulesets == ["test_ruleset"]
    assert command_object.validate_options.use_bundled_rulesets
    assert command_object.validate_options.extra_rule_dirs == [Path(".")]
    assert command_object.validate_options.apply_generic
    assert not command_object.validate_options.use_pdb
    assert command_object.validate_options.rule_filter.name == ["homogeneous_time"]
    assert command_object.validate_options.rule_filter.ids == ["core_profiles"]


def test_explore_command():
    argv = ["explore"]

    imas_validator_cli.main(argv)
