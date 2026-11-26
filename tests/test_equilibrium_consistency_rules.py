"""Tests for the equilibrium consistency rules on an analytic Solov'ev equilibrium with elliptical contours in (R**2, Z)."""

import copy
import re

import imas  # type: ignore
import numpy as np
import pytest

from imas_validator.validate.validate import validate
from imas_validator.validate_options import RuleFilter, ValidateOptions

DD3 = "3.40.1"
DD4 = "4.0.0"
R0, A, KAPPA = 6.2, 2.0, 1.7
PSI_AXIS = 10.0
F_B = -33.0
RULES = [
    "validate_pressure_consistency",
    "validate_f_consistency",
    "validate_q_phi_consistency",
    "validate_rho_tor_norm_consistency",
    "validate_q_global_consistency",
    "validate_j_tor_ip_consistency",
    "validate_psi_2d_consistency",
    "validate_geometry_2d_consistency",
    "validate_psi_range_consistency",
]


def current_density_name(dd_version):
    return "j_tor" if dd_version.startswith("3") else "j_phi"


def make_equilibrium(dd_version, n=101, nr=65, nz=129):
    span = -2.0 if dd_version == DD3 else 2.0  # negative Ip in both COCOS
    width, height = 2 * R0 * A, KAPPA * A
    x = np.linspace(0.0, 1.0, n)
    psi = PSI_AXIS + span * x
    theta = np.linspace(0, 2 * np.pi, 512, endpoint=False)
    radius = np.sqrt(R0**2 + width * np.sqrt(x[:, None]) * np.cos(theta))
    # psi = axis + span * (((R**2-R0**2)/width)**2 + (Z/height)**2).
    # Delta*psi = span * (8 R**2/width**2 + 2/height**2).
    mu0 = 4e-7 * np.pi
    dp = -8 * span / (width**2 * (2 * np.pi) ** 2 * mu0)
    ffp = -2 * span / (height**2 * (2 * np.pi) ** 2)
    f = -np.sqrt(F_B**2 + 2 * ffp * span * (x - 1))
    q = (
        abs(f)
        * np.pi
        * width
        * height
        / (2 * abs(span) * np.sqrt(R0**4 - width**2 * x))
    )
    phi = -abs(span) * np.r_[0, np.cumsum(0.5 * (q[1:] + q[:-1]) * np.diff(x))]
    # Cross-sectional area by Green's theorem; dA/dx weights j_phi by 1/R.
    area = 2 * np.pi * height * np.sqrt(x) * np.mean(radius * np.cos(theta), axis=1)
    volume = np.pi**2 * width * height * x
    j_local = (
        -abs(span)
        * (8 * radius**2 / width**2 + 2 / height**2)
        / (2 * np.pi * mu0 * radius)
    )
    j = np.mean(j_local / radius, axis=1) / np.mean(1 / radius, axis=1)
    ip = np.sum(0.5 * (j[1:] + j[:-1]) * np.diff(area))

    eq = imas.IDSFactory(dd_version).equilibrium()
    eq.ids_properties.homogeneous_time = 1
    eq.time = [0.0]
    eq.vacuum_toroidal_field.r0 = R0
    eq.vacuum_toroidal_field.b0 = [F_B / R0]
    eq.time_slice.resize(1)
    ts = eq.time_slice[0]
    gq = ts.global_quantities
    gq.ip = ip
    gq.psi_axis, gq.psi_boundary = PSI_AXIS, PSI_AXIS + span
    gq.magnetic_axis.r, gq.magnetic_axis.z = R0, 0.0
    gq.q_axis, gq.q_95 = q[0], np.interp(0.95, x, q)
    p1 = ts.profiles_1d
    p1.psi = psi
    p1.pressure = dp * span * (x - 1)
    p1.dpressure_dpsi = np.full(n, dp)
    p1.f = f
    p1.f_df_dpsi = np.full(n, ffp)
    p1.q = q
    p1.phi = phi
    p1.rho_tor_norm = np.sqrt(phi / phi[-1])
    p1.area = area
    p1.volume = volume
    setattr(p1, current_density_name(dd_version), j)
    theta = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    ts.boundary.outline.r = np.sqrt(R0**2 + width * np.cos(theta))
    ts.boundary.outline.z = KAPPA * A * np.sin(theta)
    ts.profiles_2d.resize(1)
    p2 = ts.profiles_2d[0]
    p2.grid_type.index = 1
    r = np.linspace(3.0, 9.5, nr)
    z = np.linspace(-5.0, 5.0, nz)
    rr, zz = np.meshgrid(r, z, indexing="ij")
    p2.grid.dim1, p2.grid.dim2 = r, z
    p2.psi = PSI_AXIS + span * (
        ((rr**2 - R0**2) / width) ** 2 + (zz / (KAPPA * A)) ** 2
    )
    return eq


def run_rules(tmp_path, dd_version, eq):
    uri = f"{tmp_path}/equilibrium.nc"
    with imas.DBEntry(uri, "w", dd_version=dd_version) as dbentry:
        dbentry.put(eq)
    options = ValidateOptions(rule_filter=RuleFilter(name=["equilibrium_consistency"]))
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("IMAS_VERSION", dd_version)
        results = validate(uri, validate_options=options).results
    for result in results:
        assert result.exc is None, f"{result.rule.name} raised {result.exc!r}"
    return results


def rule_names(results, success=None):
    return {
        result.rule.name.split(":")[-1]
        for result in results
        if success is None or result.success == success
    }


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_consistent_equilibrium_passes(tmp_path, dd_version):
    results = run_rules(tmp_path, dd_version, make_equilibrium(dd_version))
    assert rule_names(results, success=False) == set()
    assert rule_names(results) == set(RULES)


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize(
    "rule, perturb",
    [
        (
            "validate_pressure_consistency",
            lambda p1, ts: setattr(p1, "pressure", 1.05 * p1.pressure),
        ),
        (
            "validate_f_consistency",
            lambda p1, ts: setattr(p1, "f_df_dpsi", 1.1 * p1.f_df_dpsi),
        ),
        ("validate_q_phi_consistency", lambda p1, ts: setattr(p1, "q", 1.05 * p1.q)),
        (
            "validate_rho_tor_norm_consistency",
            lambda p1, ts: setattr(p1, "rho_tor_norm", np.sqrt(p1.rho_tor_norm)),
        ),
        (
            "validate_q_global_consistency",
            lambda p1, ts: setattr(
                ts.global_quantities, "q_95", 1.05 * ts.global_quantities.q_95
            ),
        ),
        (
            "validate_j_tor_ip_consistency",
            lambda p1, ts: setattr(
                ts.global_quantities, "ip", 1.05 * ts.global_quantities.ip
            ),
        ),
        (
            "validate_psi_2d_consistency",
            lambda p1, ts: setattr(
                ts.profiles_2d[0], "psi", ts.profiles_2d[0].psi + 0.1
            ),
        ),
        (
            "validate_geometry_2d_consistency",
            lambda p1, ts: setattr(p1, "volume", 1.05 * p1.volume),
        ),
    ],
)
def test_inconsistent_equilibrium_fails(tmp_path, dd_version, rule, perturb):
    eq = make_equilibrium(dd_version)
    ts = eq.time_slice[0]
    perturb(ts.profiles_1d, ts)
    results = run_rules(tmp_path, dd_version, eq)
    assert rule in rule_names(results, success=False)


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_only_the_perturbed_check_fails(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    eq.time_slice[0].profiles_1d.pressure = 1.05 * eq.time_slice[0].profiles_1d.pressure
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results, success=False) == {"validate_pressure_consistency"}


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_not_filled_is_skipped(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    ts = eq.time_slice[0]
    ts.profiles_2d.resize(0)
    ts.profiles_1d.dpressure_dpsi = []
    results = run_rules(tmp_path, dd_version, eq)
    names = rule_names(results)
    assert "validate_pressure_consistency" not in names
    assert "validate_psi_2d_consistency" not in names
    assert "validate_geometry_2d_consistency" not in names
    assert rule_names(results, success=False) == set()


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_slice_without_equilibrium_is_skipped(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    gq = eq.time_slice[0].global_quantities
    gq.psi_boundary = gq.psi_axis  # e.g. a time slice before the first solve
    eq.time_slice[0].profiles_1d.pressure = 2 * eq.time_slice[0].profiles_1d.pressure
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results) == set()


def failure_paths(results, rule):
    """IDS paths recorded by the failed asserts of ``rule``"""
    return {
        path
        for result in results
        if not result.success and result.rule.name.endswith(rule)
        for paths in result.nodes_dict.values()
        for path in paths
    }


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_coarse_2d_grid_passes(tmp_path, dd_version):
    # the bilinear interpolation error of a 33x33 map is ~1.5% in volume at
    # psi_norm = 0.3: it must widen the tolerance instead of failing
    results = run_rules(
        tmp_path, dd_version, make_equilibrium(dd_version, nr=33, nz=33)
    )
    assert "validate_geometry_2d_consistency" in rule_names(results)
    assert rule_names(results, success=False) == set()


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_coarse_2d_grid_still_detects_inconsistency(tmp_path, dd_version):
    eq = make_equilibrium(dd_version, nr=33, nz=33)
    eq.time_slice[0].profiles_1d.volume = 1.1 * eq.time_slice[0].profiles_1d.volume
    results = run_rules(tmp_path, dd_version, eq)
    assert "validate_geometry_2d_consistency" in rule_names(results, success=False)


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_profiles_not_reaching_boundary(tmp_path, dd_version):
    # consistent profiles truncated at psi_norm = 0.5: whole-plasma checks are
    # skipped and the others only use the covered range
    eq = make_equilibrium(dd_version)
    p1 = eq.time_slice[0].profiles_1d
    keep = np.linspace(0.0, 1.0, len(p1.psi)) <= 0.5 + 1e-9
    for name in [
        "psi",
        "pressure",
        "dpressure_dpsi",
        "f",
        "f_df_dpsi",
        "q",
        "phi",
        "rho_tor_norm",
        "area",
        "volume",
        current_density_name(dd_version),
    ]:
        setattr(p1, name, np.asarray(getattr(p1, name))[keep])
    results = run_rules(tmp_path, dd_version, eq)
    names = rule_names(results)
    assert "validate_j_tor_ip_consistency" not in names
    assert "validate_rho_tor_norm_consistency" not in names
    assert "validate_geometry_2d_consistency" in names
    assert rule_names(results, success=False) == set()


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_psi_2d_checked_without_profiles_1d(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    for name in [
        "psi",
        "pressure",
        "dpressure_dpsi",
        "f",
        "f_df_dpsi",
        "q",
        "phi",
        "rho_tor_norm",
        "area",
        "volume",
        current_density_name(dd_version),
    ]:
        setattr(eq.time_slice[0].profiles_1d, name, [])
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results) == {"validate_psi_2d_consistency"}
    assert rule_names(results, success=False) == set()

    p2 = eq.time_slice[0].profiles_2d[0]
    p2.psi = p2.psi + 0.1  # 5% of the psi range
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results, success=False) == {"validate_psi_2d_consistency"}


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize("flip", ["r", "z", "rz"])
def test_descending_2d_grid(tmp_path, dd_version, flip):
    eq = make_equilibrium(dd_version)
    p2 = eq.time_slice[0].profiles_2d[0]
    r, z, psi = np.asarray(p2.grid.dim1), np.asarray(p2.grid.dim2), np.asarray(p2.psi)
    if "r" in flip:
        r, psi = r[::-1], psi[::-1, :]
    if "z" in flip:
        z, psi = z[::-1], psi[:, ::-1]
    p2.grid.dim1, p2.grid.dim2, p2.psi = r, z, psi
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results, success=False) == set()

    p2.psi = psi + 0.1
    results = run_rules(tmp_path, dd_version, eq)
    assert "validate_psi_2d_consistency" in rule_names(results, success=False)


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_failure_reports_all_inputs(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    eq.time_slice[0].profiles_1d.pressure = 1.05 * eq.time_slice[0].profiles_1d.pressure
    results = run_rules(tmp_path, dd_version, eq)
    paths = failure_paths(results, "validate_pressure_consistency")
    for name in ["pressure", "dpressure_dpsi", "psi"]:
        assert f"time_slice[0]/profiles_1d/{name}" in paths


def test_grid_not_covering_the_outline(tmp_path):
    # the outboard half of the map is missing: checks that would extrapolate are
    # skipped instead of failing
    eq = make_equilibrium(DD4)
    p2 = eq.time_slice[0].profiles_2d[0]
    keep = p2.grid.dim1.value <= R0
    p2.psi = p2.psi.value[keep, :]
    p2.grid.dim1 = p2.grid.dim1.value[keep]
    results = run_rules(tmp_path, DD4, eq)
    assert "validate_geometry_2d_consistency" not in rule_names(results)
    assert rule_names(results, success=False) == set()


def with_slices(eq, n):
    """Copy the single time slice of ``eq`` to ``n`` slices."""
    first = copy.deepcopy(eq.time_slice[0])
    eq.time_slice.resize(n, keep=True)
    for i in range(1, n):
        eq.time_slice[i] = copy.deepcopy(first)
    eq.time = np.arange(n, dtype=float)
    eq.vacuum_toroidal_field.b0 = np.full(n, eq.vacuum_toroidal_field.b0.value[0])
    return eq


def checked_slices(results, rule):
    return {
        int(index)
        for result in results
        if result.rule.name.endswith(rule)
        for paths in result.nodes_dict.values()
        for path in paths
        for index in re.findall(r"time_slice\[(\d+)\]", path)
    }


@pytest.mark.parametrize("n, expected", [(20, 20), (25, 20)])
def test_2d_checks_sample_slices(tmp_path, n, expected):
    eq = with_slices(make_equilibrium(DD3, nr=33, nz=33), n)
    results = run_rules(tmp_path, DD3, eq)
    for rule in ["validate_geometry_2d_consistency", "validate_psi_2d_consistency"]:
        assert len(checked_slices(results, rule)) == expected
    assert rule_names(results, success=False) == set()


@pytest.mark.parametrize("bad", [np.nan, -9e40])
def test_invalid_q_on_the_separatrix(tmp_path, bad):
    eq = make_equilibrium(DD3)
    q = eq.time_slice[0].profiles_1d.q.value.copy()
    q[-1] = bad
    eq.time_slice[0].profiles_1d.q = q
    results = run_rules(tmp_path, DD3, eq)
    assert "validate_q_phi_consistency" in rule_names(results)
    assert "validate_q_global_consistency" in rule_names(results)
    assert rule_names(results, success=False) == set()


def test_invalid_ip_is_skipped(tmp_path):
    eq = make_equilibrium(DD3)
    eq.time_slice[0].global_quantities.ip = np.nan
    assert rule_names(run_rules(tmp_path, DD3, eq)) == set()


@pytest.mark.parametrize("dd_version", [DD3, DD4])
@pytest.mark.parametrize("change", ["offset", "2pi"])
def test_psi_of_profiles_1d_not_matching_global_quantities(
    tmp_path, dd_version, change
):
    eq = make_equilibrium(dd_version)
    p1 = eq.time_slice[0].profiles_1d
    if change == "offset":
        p1.psi = p1.psi.value + 5.0
    else:
        p1.psi = p1.psi.value * 2 * np.pi
    results = run_rules(tmp_path, dd_version, eq)
    assert "validate_psi_range_consistency" in rule_names(results, success=False)


def test_four_point_q_profile(tmp_path):
    eq = make_equilibrium(DD4, n=4)
    ts = eq.time_slice[0]
    ts.profiles_2d.resize(0)
    p = ts.profiles_1d
    x = np.linspace(0, 1, 4)
    p.q = 1 + 3 * x**2
    p.phi = -2 * (x + x**3)
    ts.global_quantities.q_axis = 1
    ts.global_quantities.q_95 = 1 + 3 * 0.95**2

    def q_failures():
        return rule_names(run_rules(tmp_path, DD4, eq), False) & {
            "validate_q_phi_consistency",
            "validate_q_global_consistency",
        }

    assert not q_failures()
    p.q = 1.25 * p.q
    assert q_failures() == {
        "validate_q_phi_consistency",
        "validate_q_global_consistency",
    }


def pedestal_equilibrium(grid, n, width):
    """1D profiles only, with an H-mode-like tanh pedestal at psi_norm = 0.96 in
    pressure and F**2, on a uniform psi or uniform sqrt(psi) grid."""
    eq = make_equilibrium(DD3)
    ts = eq.time_slice[0]
    ts.profiles_2d.resize(0)
    gq = ts.global_quantities
    span = float(gq.psi_boundary) - float(gq.psi_axis)
    x = np.linspace(0, 1, n) if grid == "psi" else np.linspace(0, 1, n) ** 2
    t = np.tanh((x - 0.96) / width)
    sech2 = 1 - t**2
    p1 = ts.profiles_1d
    for name in ["q", "phi", "rho_tor_norm", "area", "volume", "j_tor"]:
        setattr(p1, name, [])
    p1.psi = float(gq.psi_axis) + span * x
    p1.pressure = 6e5 * (1 - x) ** 2 + 1e5 * (1 - t) / 2
    p1.dpressure_dpsi = (-1.2e6 * (1 - x) - 1e5 * sech2 / (2 * width)) / span
    g = 30 * ((1 - x) ** 2 + 0.5 * (1 - t) / 2)  # F**2 - F_b**2
    p1.f = -np.sqrt(F_B**2 + g)
    p1.f_df_dpsi = 0.5 * 30 * (-2 * (1 - x) - 0.5 * sech2 / (2 * width)) / span
    return eq


@pytest.mark.parametrize(
    "grid, n, width", [("psi", 129, 0.01), ("sqrt", 257, 0.01), ("psi", 65, 0.02)]
)
def test_resolved_pedestal(tmp_path, grid, n, width):
    eq = pedestal_equilibrium(grid, n, width)
    results = run_rules(tmp_path, DD3, eq)
    rules = {"validate_pressure_consistency", "validate_f_consistency"}
    assert rules <= rule_names(results)
    assert rule_names(results, success=False) == set()

    p1 = eq.time_slice[0].profiles_1d
    p1.pressure = 1.05 * p1.pressure.value
    p1.f_df_dpsi = 1.1 * p1.f_df_dpsi.value
    assert rules <= rule_names(run_rules(tmp_path, DD3, eq), success=False)


def test_nan_outside_the_plasma_in_the_2d_map(tmp_path):
    eq = make_equilibrium(DD3)
    p2 = eq.time_slice[0].profiles_2d[0]
    psi = p2.psi.value.copy()
    rr, zz = np.meshgrid(p2.grid.dim1.value, p2.grid.dim2.value, indexing="ij")
    psi[np.abs(zz) > 4.5] = np.nan
    p2.psi = psi
    results = run_rules(tmp_path, DD3, eq)
    assert "validate_geometry_2d_consistency" in rule_names(results)
    assert rule_names(results, success=False) == set()


@pytest.mark.parametrize("dd_version", [DD3, DD4])
def test_profiles_from_boundary_to_axis(tmp_path, dd_version):
    eq = make_equilibrium(dd_version)
    p1 = eq.time_slice[0].profiles_1d
    names = [
        "psi",
        "pressure",
        "dpressure_dpsi",
        "f",
        "f_df_dpsi",
        "q",
        "phi",
        "rho_tor_norm",
        "area",
        "volume",
        current_density_name(dd_version),
    ]
    for name in names:
        setattr(p1, name, getattr(p1, name).value[::-1])
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results) == set(RULES)
    assert rule_names(results, success=False) == set()

    p1.pressure = 1.2 * p1.pressure.value
    results = run_rules(tmp_path, dd_version, eq)
    assert rule_names(results, success=False) == {"validate_pressure_consistency"}


def test_q_95_nan_is_skipped_and_sign_is_ignored(tmp_path):
    eq = make_equilibrium(DD3)
    gq = eq.time_slice[0].global_quantities
    gq.q_95 = np.nan
    assert rule_names(run_rules(tmp_path, DD3, eq), success=False) == set()

    p1 = eq.time_slice[0].profiles_1d
    gq.q_95 = np.interp(0.95, np.linspace(0, 1, len(p1.q)), p1.q.value)
    p1.q = -p1.q.value
    gq.q_axis = -float(gq.q_axis)
    results = run_rules(tmp_path, DD3, eq)
    assert "validate_q_global_consistency" in rule_names(results)
    assert rule_names(results, success=False) == set()
