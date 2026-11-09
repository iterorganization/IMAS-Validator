"""Tests for the generic COCOS rules (generic/cocos.py)"""

import imas  # type: ignore
import numpy as np
import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions

DD3 = "3.40.1"
DD4 = "4.0.0"
IP = 1.5e7
B0 = -5.3


def cocos_of(dd_version):
    return 11 if dd_version.startswith("3") else 17


def consistent_profiles(dd_version, ip=IP, b0=B0):
    """Return profiles that follow the COCOS of the given DD version"""
    sigma_bp = 1 if cocos_of(dd_version) == 11 else -1
    sign_ip, sign_b0 = np.sign(ip), np.sign(b0)
    return {
        "rho": np.array([0.0, 0.5, 1.0]),
        "q": sign_ip * sign_b0 * np.array([1.0, 1.5, 3.0]),
        "psi": 10.0 + sigma_bp * sign_ip * np.array([0.0, 1.0, 2.0]),
        "f": sign_b0 * np.array([33.0, 33.0, 33.0]),
        "phi": sign_b0 * np.array([0.0, 50.0, 100.0]),
        "j": sign_ip * np.array([1e6, 5e5, 1e4]),
    }


def current_density_name(dd_version):
    return "j_tor" if cocos_of(dd_version) == 11 else "j_phi"


def make_equilibrium(dd_version, prof, ip=IP, b0=B0):
    eq = imas.IDSFactory(dd_version).equilibrium()
    eq.ids_properties.homogeneous_time = 1
    eq.time = [0.0]
    eq.vacuum_toroidal_field.r0 = 6.2
    eq.vacuum_toroidal_field.b0 = [b0]
    eq.time_slice.resize(1)
    ts = eq.time_slice[0]
    ts.global_quantities.ip = ip
    ts.global_quantities.psi_axis = prof["psi"][0]
    ts.global_quantities.psi_boundary = prof["psi"][-1]
    ts.global_quantities.q_axis = prof["q"][0]
    ts.global_quantities.q_95 = prof["q"][-1]
    ts.profiles_1d.psi = prof["psi"]
    ts.profiles_1d.q = prof["q"]
    ts.profiles_1d.f = prof["f"]
    ts.profiles_1d.phi = prof["phi"]
    ts.profiles_1d.pressure = [1e5, 5e4, 0.0]
    setattr(ts.profiles_1d, current_density_name(dd_version), prof["j"])
    return eq


def make_profiles(dd_version, ids_name, prof, ip=IP, b0=B0):
    ids = imas.IDSFactory(dd_version).new(ids_name)
    ids.ids_properties.homogeneous_time = 1
    ids.time = [0.0]
    ids.vacuum_toroidal_field.r0 = 6.2
    ids.vacuum_toroidal_field.b0 = [b0]
    if hasattr(ids, "global_quantities") and hasattr(ids.global_quantities, "ip"):
        ids.global_quantities.ip = [ip]
    ids.profiles_1d.resize(1)
    p1d = ids.profiles_1d[0]
    p1d.grid.rho_tor_norm = prof["rho"]
    p1d.grid.rho_pol_norm = prof["rho"]
    p1d.grid.psi = prof["psi"]
    p1d.grid.psi_magnetic_axis = prof["psi"][0]
    p1d.grid.psi_boundary = prof["psi"][-1]
    p1d.q = prof["q"]
    if hasattr(p1d, current_density_name(dd_version)):
        setattr(p1d, current_density_name(dd_version), prof["j"])
    return ids


def make_summary(dd_version, prof, ip=IP, b0=B0):
    summary = imas.IDSFactory(dd_version).summary()
    summary.ids_properties.homogeneous_time = 1
    summary.time = [0.0]
    summary.global_quantities.ip.value = [ip]
    summary.global_quantities.b0.value = [b0]
    summary.global_quantities.q_95.value = [prof["q"][-1]]
    summary.local.magnetic_axis.q.value = [prof["q"][0]]
    return summary


def make_idss(dd_version, prof):
    idss = {
        "equilibrium": make_equilibrium(dd_version, prof),
        "core_profiles": make_profiles(dd_version, "core_profiles", prof),
        "edge_profiles": make_profiles(dd_version, "edge_profiles", prof),
        "summary": make_summary(dd_version, prof),
    }
    if cocos_of(dd_version) == 17:
        idss["plasma_profiles"] = make_profiles(dd_version, "plasma_profiles", prof)
    return idss


def run_cocos_rules(tmp_path, dd_version, idss):
    uri = f"{tmp_path}/cocos.nc"
    with imas.DBEntry(uri, "w", dd_version=dd_version) as dbentry:
        for ids in idss.values():
            dbentry.put(ids)
    options = ValidateOptions(rule_filter=RuleFilter(name=["cocos"]))
    # validate() only lists the IDSs of the default DD version: match the entry's
    # version so that DD4-only IDSs (plasma_profiles) are validated as well
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("IMAS_VERSION", dd_version)
        results = validate(uri, validate_options=options).results
    for result in results:
        assert result.exc is None, f"{result.rule.name} raised {result.exc!r}"
    return results


def failed_rules(results):
    return {result.rule.name.split(":")[-1] for result in results if not result.success}


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize("ip, b0", [(IP, B0), (-IP, B0), (IP, -B0), (-IP, -B0)])
def test_consistent_data_passes(tmp_path, dd_version, ip, b0):
    prof = consistent_profiles(dd_version, ip, b0)
    idss = {
        "equilibrium": make_equilibrium(dd_version, prof, ip, b0),
        "core_profiles": make_profiles(dd_version, "core_profiles", prof, ip, b0),
        "edge_profiles": make_profiles(dd_version, "edge_profiles", prof, ip, b0),
        "summary": make_summary(dd_version, prof, ip, b0),
    }
    results = run_cocos_rules(tmp_path, dd_version, idss)
    assert failed_rules(results) == set()

    cocos = cocos_of(dd_version)
    rule_names = {result.rule.name.split(":")[-1] for result in results}
    assert rule_names == {
        f"validate_cocos{cocos}_{name}"
        for name in ["equilibrium", "core_profiles", "edge_profiles", "summary"]
    }


def test_plasma_profiles_dd4(tmp_path):
    prof = consistent_profiles(DD4)
    idss = {"plasma_profiles": make_profiles(DD4, "plasma_profiles", prof)}
    results = run_cocos_rules(tmp_path, DD4, idss)
    assert len(results) > 0
    assert failed_rules(results) == set()

    prof["psi"] = prof["psi"][::-1]
    idss = {"plasma_profiles": make_profiles(DD4, "plasma_profiles", prof)}
    results = run_cocos_rules(tmp_path, DD4, idss)
    assert failed_rules(results) == {"validate_cocos17_plasma_profiles"}


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "ids_name, field",
    [
        ("equilibrium", "psi"),
        ("equilibrium", "q"),
        ("equilibrium", "f"),
        ("equilibrium", "phi"),
        ("equilibrium", "j"),
        ("core_profiles", "psi"),
        ("core_profiles", "q"),
        ("core_profiles", "j"),
        ("edge_profiles", "psi"),
        ("summary", "q"),
    ],
)
def test_flipped_sign_fails(tmp_path, dd_version, ids_name, field):
    prof = consistent_profiles(dd_version)
    idss = make_idss(dd_version, prof)
    flipped = dict(prof)
    if field == "psi":
        flipped["psi"] = prof["psi"][::-1]
    else:
        flipped[field] = -prof[field]
    idss[ids_name] = make_idss(dd_version, flipped)[ids_name]

    results = run_cocos_rules(tmp_path, dd_version, idss)
    assert failed_rules(results) == {f"validate_cocos{cocos_of(dd_version)}_{ids_name}"}


def test_dd3_convention_in_dd4_entry_fails(tmp_path):
    # psi following COCOS 11 stored in a DD4 (COCOS 17) entry
    prof = consistent_profiles(DD4)
    prof["psi"] = consistent_profiles(DD3)["psi"]
    idss = make_idss(DD4, prof)
    results = run_cocos_rules(tmp_path, DD4, idss)
    assert failed_rules(results) == {
        "validate_cocos17_equilibrium",
        "validate_cocos17_core_profiles",
        "validate_cocos17_edge_profiles",
        "validate_cocos17_plasma_profiles",
    }


def test_unknown_reference_signs_are_skipped(tmp_path):
    prof = consistent_profiles(DD3)
    prof["psi"] = prof["psi"][::-1]  # wrong, but no Ip to compare with
    eq = make_equilibrium(DD3, prof, ip=0.0, b0=B0)
    results = run_cocos_rules(tmp_path, DD3, {"equilibrium": eq})
    assert failed_rules(results) == set()


@pytest.mark.parametrize(
    "version, cocos",
    [
        ("3.22.0", 11),
        ("3.42.0", 11),
        ("3.99.1.dev3+gabc", 11),
        ("4.0.0rc1", 17),
        ("4.0.0", 17),
        ("4.1.1.dev12+gabc", 17),
    ],
)
def test_version_specifiers(version, cocos):
    dd3, dd4 = SpecifierSet("<4.0.0.dev0"), SpecifierSet(">=4.0.0.dev0")
    assert (Version(version) in dd3) == (cocos == 11)
    assert (Version(version) in dd4) == (cocos == 17)
