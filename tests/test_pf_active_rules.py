"""Tests for the pf_active limit rules (generic/pf_active.py and iter/pf_active.py)"""

import ast
from pathlib import Path

import imas  # type: ignore
import numpy as np
import pytest
from imas.ids_defs import EMPTY_FLOAT  # type: ignore

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions

DD3 = "3.40.1"
DD4 = "4.0.0"
ITER_RULES = (
    Path(__file__).parents[1] / "imas_validator/assets/rulesets/iter/pf_active.py"
)
# ITER machine description pf_active entry with the power supplies in their
# full configuration, which applies from SRO on (see iter/pf_active.py)
ITER_MD = "/work/imas/shared/imasdb/ITER_MD/3/111001/204"
CS_LIMIT = ([12.6, 13.0], [4.3], [[45000.0], [40000.0]])


def new_pf_active(dd_version, n_time=3):
    pf = imas.IDSFactory(dd_version).pf_active()
    pf.ids_properties.homogeneous_time = 1
    pf.time = np.arange(n_time, dtype=float)
    return pf


def add_coil(pf, name, current, limit=None, b_field=None):
    pf.coil.resize(len(pf.coil) + 1, keep=True)
    coil = pf.coil[-1]
    coil.name = name
    coil.current.data = current
    if limit is not None:
        coil.b_field_max, coil.temperature, coil.current_limit_max = limit
    if b_field is not None:
        coil.b_field_max_timed.data = b_field
    return coil


def run_rules(tmp_path, dd_version, ids, name):
    uri = f"{tmp_path}/pf_active.nc"
    with imas.DBEntry(uri, "w", dd_version=dd_version) as dbentry:
        dbentry.put(ids)
    options = ValidateOptions(rule_filter=RuleFilter(name=[name]))
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("IMAS_VERSION", dd_version)
        results = validate(uri, validate_options=options).results
    for result in results:
        assert result.exc is None, f"{result.rule.name} raised {result.exc!r}"
    return results


def outcome(results, rule):
    """Return None when the rule made no assert, else whether all asserts passed"""
    selected = [r for r in results if r.rule.name.endswith(f":{rule}")]
    return None if not selected else all(r.success for r in selected)


# Generic rules


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "current, b_field, expected",
    [
        ([0.0, 30e3, -44e3], None, True),
        ([0.0, 30e3, -46e3], None, False),  # above the largest tabulated limit
        ([0.0, 30e3, -44e3], [12.0, 12.6, 12.6], True),
        ([0.0, 30e3, -44e3], [12.0, 12.6, 13.0], False),  # 40 kA at 13 T
        ([0.0, 30e3, -39e3], [12.0, 12.6, 13.08], True),  # 39 kA at 13.08 T
        ([0.0, 30e3, -39e3], [12.0, 12.6, 13.1], False),  # extrapolated: 38.75 kA
        ([0.0, 46e3, -44e3], [12.0, 12.5, 12.6], True),  # 46.25 kA at 12.5 T
    ],
)
def test_coil_current_limit(tmp_path, dd_version, current, b_field, expected):
    pf = new_pf_active(dd_version)
    add_coil(pf, "CS3U", current, CS_LIMIT, b_field)
    results = run_rules(tmp_path, dd_version, pf, "validate_coil_current_limit")
    assert outcome(results, "validate_coil_current_limit") is expected


def test_coil_current_limit_most_permissive_temperature(tmp_path):
    pf6 = ([6.4, 7.0], [3.9, 4.3], [[52000.0, 48000.0], [41000.0, 0.0]])
    pf = new_pf_active(DD3)
    add_coil(pf, "PF6", [0.0, 50e3, 40e3], pf6, [6.0, 6.4, 7.0])
    results = run_rules(tmp_path, DD3, pf, "validate_coil_current_limit")
    assert outcome(results, "validate_coil_current_limit") is True


def test_coil_current_limit_not_filled(tmp_path):
    pf = new_pf_active(DD3)
    add_coil(pf, "CS3U", [0.0, 1e6, 1e6])
    add_coil(pf, "CS2U", [], CS_LIMIT)
    results = run_rules(tmp_path, DD3, pf, "validate_coil_current_limit")
    assert outcome(results, "validate_coil_current_limit") is None


def test_coil_current_limit_not_applied_to_ampere_turns(tmp_path):
    # Before DD 3.32.1, coil/current was the total current of the coil
    pf = new_pf_active("3.31.0")
    add_coil(pf, "CS3U", [0.0, 20e6, 20e6], CS_LIMIT)
    results = run_rules(tmp_path, "3.31.0", pf, "validate_coil_current_limit")
    assert outcome(results, "validate_coil_current_limit") is None


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "limits, voltage, expected",
    [
        ((-2100.0, 2100.0), [0.0, 2000.0, -2000.0], True),
        ((-2100.0, 2100.0), [0.0, 2200.0, -2000.0], False),
        ((-2100.0, 2100.0), [0.0, 2000.0, -2200.0], False),
        ((EMPTY_FLOAT, 2100.0), [0.0, 2000.0, -5000.0], True),  # no lower limit
        ((EMPTY_FLOAT, EMPTY_FLOAT), [0.0, 9000.0, -9000.0], None),
    ],
)
def test_supply_voltage_limits(tmp_path, dd_version, limits, voltage, expected):
    pf = new_pf_active(dd_version)
    pf.supply.resize(1)
    pf.supply[0].name = "CS3U-1-2"
    pf.supply[0].voltage_limit_min, pf.supply[0].voltage_limit_max = limits
    pf.supply[0].voltage.data = voltage
    results = run_rules(tmp_path, dd_version, pf, "validate_supply_limits")
    assert outcome(results, "validate_supply_limits") is expected


def test_supply_current_limits(tmp_path):
    pf = new_pf_active(DD3)
    pf.supply.resize(1)
    pf.supply[0].name = "PF1-1-2"
    pf.supply[0].current_limit_min = -48000.0
    pf.supply[0].current_limit_max = 48000.0
    pf.supply[0].current.data = [0.0, 47e3, -49e3]
    results = run_rules(tmp_path, DD3, pf, "validate_supply_limits")
    assert outcome(results, "validate_supply_limits") is False


def make_force_pf_active(dd_version, f_vertical, limit_min, limit_max):
    """Two coils, limit 0 on the sum of their vertical forces, limit 1 on the
    radial force of the first coil"""
    pf = new_pf_active(dd_version, n_time=2)
    for i, name in enumerate(["PF1", "PF2"]):
        coil = add_coil(pf, name, [0.0, 0.0])
        coil.force_radial.data = [0.0, 1e6]
        coil.force_vertical.data = f_vertical[i]
    matrix = np.zeros((2, 8))
    matrix[0, [1, 5]] = 1.0
    matrix[1, 0] = 1.0
    pf.force_limits.combination_matrix = matrix
    pf.force_limits.limit_min = limit_min
    pf.force_limits.limit_max = limit_max
    return pf


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "f_vertical, limit_min, limit_max, expected",
    [
        ([[0.0, 5e6], [0.0, 4e6]], [-1e7, 0.0], [1e7, 2e6], True),
        ([[0.0, 6e6], [0.0, 5e6]], [-1e7, 0.0], [1e7, 2e6], False),
        ([[0.0, -6e6], [0.0, -5e6]], [-1e7, 0.0], [1e7, 2e6], False),
        ([[0.0, 6e6], [0.0, 5e6]], [-1e7, 0.0], [EMPTY_FLOAT, 2e6], True),
        ([[0.0, 1e6], [0.0, 1e6]], [-1e7, 2e6], [1e7, 2e6], False),  # radial
    ],
)
def test_force_limits(tmp_path, dd_version, f_vertical, limit_min, limit_max, expected):
    pf = make_force_pf_active(dd_version, f_vertical, limit_min, limit_max)
    results = run_rules(tmp_path, dd_version, pf, "validate_force_limits")
    assert outcome(results, "validate_force_limits") is expected


def test_force_limits_missing_force(tmp_path):
    pf = make_force_pf_active(DD3, [[0.0, 6e6], []], [-1e7, -1e7], [1e7, 1e7])
    results = run_rules(tmp_path, DD3, pf, "validate_force_limits")
    # Only the radial force limit can be evaluated
    selected = [r for r in results if r.rule.name.endswith(":validate_force_limits")]
    assert all(r.success for r in selected)
    assert any("force_radial" in str(r.nodes_dict) for r in selected)
    assert not any("force_vertical" in str(r.nodes_dict) for r in selected)


def test_force_limits_wrong_number_of_columns(tmp_path):
    pf = make_force_pf_active(DD3, [[0.0, 1.0], [0.0, 1.0]], [-1e7, -1e7], [1e7, 1e7])
    pf.force_limits.combination_matrix = np.zeros((2, 6))
    results = run_rules(tmp_path, DD3, pf, "validate_force_limits")
    assert outcome(results, "validate_force_limits") is False


# ITER rules


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "name, current, expected",
    [
        ("CS3U", [0.0, 44e3], True),
        ("CS3U", [0.0, -46e3], False),
        ("CS1", [0.0, 44e3], True),  # CS1U and CS1L in series
        ("CS1", [0.0, 46e3], False),
        ("Poloidal Field Coil 6 (PF6)", [0.0, 47e3], True),
        ("Poloidal Field Coil 6 (PF6)", [0.0, 50e3], False),  # supply limit 48 kA
        ("PF5", [0.0, 54e3], False),  # conductor limit 52 kA
        ("VS3", [0.0, 1e6], None),  # not checked
    ],
)
def test_iter_coil_current(tmp_path, dd_version, name, current, expected):
    pf = new_pf_active(dd_version, n_time=2)
    add_coil(pf, name, current)
    results = run_rules(tmp_path, dd_version, pf, "iter/pf_active.py")
    assert outcome(results, "validate_coil_current") is expected


def test_iter_coil_current_b_field(tmp_path):
    pf = new_pf_active(DD3, n_time=2)
    add_coil(pf, "PF5", [0.0, 40e3], b_field=[5.0, 6.0])  # 33 kA at 6 T
    results = run_rules(tmp_path, DD3, pf, "iter/pf_active.py")
    assert outcome(results, "validate_coil_current") is False


def test_iter_coil_current_extrapolated(tmp_path):
    # PF1: 48 kA at 6.4 T and 41 kA at 6.5 T, so 34 kA at 6.6 T
    pf = new_pf_active(DD3, n_time=2)
    add_coil(pf, "PF1", [33e3, 35e3], b_field=[6.6, 6.6])
    results = run_rules(tmp_path, DD3, pf, "iter/pf_active.py")
    selected = [r for r in results if r.rule.name.endswith(":validate_coil_current")]
    assert [r.success for r in selected] == [False, True]  # conductor, supply


@pytest.mark.parametrize(
    "currents, expected",
    [
        ((40e3, 30e3, 40e3, 20e3), True),  # 10 kA
        ((40e3, 30e3, 20e3, 20e3), False),  # 30 kA
        ((-40e3, -30e3, -20e3, -20e3), False),  # -30 kA
        ((40e3, 30e3, 20e3, None), None),  # PF5 missing
    ],
)
def test_iter_imbalance_current(tmp_path, currents, expected):
    pf = new_pf_active(DD3, n_time=2)
    for name, current in zip(["PF2", "PF3", "PF4", "PF5"], currents):
        if current is not None:
            add_coil(pf, name, [0.0, current])
    results = run_rules(tmp_path, DD3, pf, "iter/pf_active.py")
    assert outcome(results, "validate_imbalance_current") is expected


def test_iter_coil_current_identifier(tmp_path):
    pf = new_pf_active(DD3, n_time=2)
    coil = add_coil(pf, "Some long name", [0.0, 50e3])
    coil.identifier = "PF1"
    results = run_rules(tmp_path, DD3, pf, "iter/pf_active.py")
    assert outcome(results, "validate_coil_current") is False


@pytest.mark.parametrize(
    "forces, expected",
    [
        ({"PF1": 1e8}, True),
        ({"PF1": 1.2e8}, False),
        ({"PF3": -5e7, "PF4": 5e7}, True),
        ({"PF3": 3e7, "PF4": -1e7}, False),  # PF3+PF4 above 10 MN
        ({c: 1.1e7 for c in ["CS3U", "CS2U", "CS1U", "CS1L", "CS2L", "CS3L"]}, False),
        ({c: 1.1e7 for c in ["CS3U", "CS2U", "CS1", "CS2L", "CS3L"]}, True),
        ({c: 1.3e7 for c in ["CS3U", "CS2U", "CS1", "CS2L", "CS3L"]}, False),
        ({c: 1.1e8 for c in ["CS3U", "CS2U", "CS2L", "CS3L"]}, None),  # no CS1
    ],
)
def test_iter_vertical_force(tmp_path, forces, expected):
    pf = new_pf_active(DD3, n_time=2)
    for name, force in forces.items():
        coil = add_coil(pf, name, [0.0, 0.0])
        coil.force_vertical.data = [0.0, force]
    results = run_rules(tmp_path, DD3, pf, "iter/pf_active.py")
    assert outcome(results, "validate_vertical_force") is expected


def iter_constants():
    """Read the constants of iter/pf_active.py without running the rule file"""
    tree = ast.parse(ITER_RULES.read_text())
    names = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            names[node.targets[0].id] = node.value
    constants = {"_CS": ast.literal_eval(names["_CS"])}
    for name in ["COIL_CURRENT_LIMITS", "SUPPLY_CURRENT_LIMITS"]:
        source = ast.unparse(names[name])
        constants[name] = eval(source, {}, dict(constants))
    stack = ast.literal_eval(names["CS_STACK"])
    source = ast.unparse(names["VERTICAL_FORCE_LIMITS"])
    constants["VERTICAL_FORCE_LIMITS"] = eval(source, {}, {"CS_STACK": stack})
    return constants


@pytest.mark.skipif(
    not Path(ITER_MD).is_dir(), reason="ITER machine description not available"
)
def test_iter_constants_match_machine_description():
    """The limits hard-coded in iter/pf_active.py must match the ITER MD"""
    with imas.DBEntry(f"imas:hdf5?path={ITER_MD}", "r") as dbentry:
        md = dbentry.get("pf_active", autoconvert=False)
    constants = iter_constants()

    coils = {str(coil.identifier): coil for coil in md.coil}
    for name, (b_field, temperature, limit) in constants["COIL_CURRENT_LIMITS"].items():
        coil = coils[name]
        assert np.array_equal(coil.b_field_max, b_field), name
        assert np.array_equal(coil.temperature, temperature), name
        assert np.array_equal(coil.current_limit_max, limit), name

    supplies = {str(s.identifier).split("-")[0]: s for s in md.supply}
    for name, limit in constants["SUPPLY_CURRENT_LIMITS"].items():
        assert supplies[name].current_limit_max == limit, name
        assert supplies[name].current_limit_min == -limit, name

    # Each vertical force limit is a row of force_limits with weight 1 on the
    # vertical force of its coils and zero elsewhere.
    fl = md.force_limits
    index = {str(coil.identifier): i for i, coil in enumerate(md.coil)}
    rows = {}
    for label, (names, lower, upper) in constants["VERTICAL_FORCE_LIMITS"].items():
        expected = np.zeros(fl.combination_matrix.shape[1])
        expected[[4 * index[name] + 1 for name in names]] = 1.0
        matches = [
            i
            for i, row in enumerate(fl.combination_matrix)
            if np.array_equal(row, expected)
        ]
        assert len(matches) == 1, label
        i = matches[0]
        rows[label] = i
        assert fl.limit_min[i] == lower, label
        assert fl.limit_max[i] == upper, label
    # All purely vertical limits of the MD are covered
    for i, row in enumerate(fl.combination_matrix):
        vertical_only = all(row[j] in (0.0, 1.0) for j in range(len(row))) and all(
            row[j] == 0.0 for j in range(len(row)) if j % 4 != 1
        )
        if vertical_only:
            assert i in rows.values(), f"force_limits row {i} not in ITER rules"
