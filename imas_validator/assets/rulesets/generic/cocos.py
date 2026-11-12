"""Generic rules verifying the COCOS sign conventions of IDSs.

The target COCOS is set by the major version of the Data Dictionary of the stored
IDS: COCOS 11 for DD3 and COCOS 17 for DD4. The rules come in pairs: the
``version`` specifier of each validator selects the rule for the right DD version.

The checks are sign relations from O. Sauter and S. Yu. Medvedev, "Tokamak
coordinate conventions: COCOS", Comput. Phys. Commun. 184 (2013) 293:

- sign(q) = sigma_rhothetaphi * sign(Ip) * sign(B0)
- sign(psi_boundary - psi_axis) = sigma_Bp * sign(Ip)
- sign(F) = sign(phi) = sign(B0)
- sign(j_tor) = sign(Ip) (sign of the profile average)

Zero, NaN and fill (-9e40) values are ignored, and so are time slices where the
sign of Ip or B0 is not known.

The rules are declared lazy, but an IDS is only lazy loaded when all rules applied
to it are lazy. In a default run the other generic rules need a full load, so the
speed-up only applies when the COCOS rules are selected alone (``--filter cocos``).
"""

import numpy as np
from imas.ids_defs import EMPTY_FLOAT

# Sign parameters of the COCOS conventions used by the Data Dictionary
COCOS = {
    11: {"sigma_bp": 1, "sigma_rhothetaphi": 1},
    17: {"sigma_bp": -1, "sigma_rhothetaphi": 1},
}
# psi differences below this fraction of |psi| are ignored (degenerate cases)
PSI_RTOL = 1e-6
DD3 = "<4.0.0.dev0"
DD4 = ">=4.0.0.dev0"


def get_field(node, path):
    """Return the filled field at ``path`` (``a/b/c``) below ``node``, or None if
    it does not exist in this DD version or has no value."""
    for name in path.split("/"):
        if not hasattr(node, name):
            return None
        node = getattr(node, name)
    return node if node.has_value else None


def slice_time(ids, aos, itime):
    """Return the time of element ``itime`` of a time-dependent array of
    structures, or None if it is not known."""
    if ids.ids_properties.homogeneous_time == 1:
        if ids.time.has_value and itime < len(ids.time):
            return ids.time[itime]
        return None
    return get_field(aos[itime], "time")


def value_at(ids, signal, itime, time):
    """Return the value of a signal stored on ``ids.time`` at the time of slice
    ``itime``, or None if it cannot be determined."""
    if signal is None:
        return None
    if len(signal) == 1:
        return signal[0]
    if not ids.time.has_value or len(ids.time) != len(signal):
        return None
    if ids.ids_properties.homogeneous_time == 1:
        return signal[itime] if itime < len(signal) else None
    if time is None:
        return None
    return np.interp(time, ids.time, signal)


def missing(values):
    """Return where ``values`` are NaN or the IMAS fill value."""
    return np.logical_or(np.isnan(values), np.isclose(values, EMPTY_FLOAT))


def reference_sign(value):
    """Return the sign (+1 or -1) of a reference quantity, or None if it is
    missing, zero, NaN or the fill value."""
    if value is None or missing(value):
        return None
    sign = np.sign(value)
    if not sign == 1 and not sign == -1:
        return None
    return sign


def mean_sign(values):
    """Return the sign of the average of the valid (non-NaN, non-fill) values,
    or None if there is none or the average is zero."""
    valid = np.where(missing(values), np.nan, values)
    if np.all(np.isnan(valid)):
        return None
    return reference_sign(np.nanmean(valid))


def check_sign(values, expected, msg):
    """Assert that all non-zero, non-NaN, non-fill ``values`` have the
    ``expected`` sign."""
    if values is None:
        return
    ignored = np.logical_or(values == 0, missing(values))
    assert np.logical_or(ignored, np.sign(values) == expected), msg


def check_psi_direction(psi_axis, psi_boundary, expected, msg):
    """Assert that sign(psi_boundary - psi_axis) equals ``expected``."""
    if psi_axis is None or psi_boundary is None:
        return
    if missing(psi_axis) or missing(psi_boundary):
        return
    diff = psi_boundary - psi_axis
    scale = np.maximum(np.abs(psi_axis), np.abs(psi_boundary))
    if np.abs(diff) <= PSI_RTOL * scale:
        return
    assert np.sign(diff) == expected, msg


def check_psi_profile(psi, expected, msg):
    """Assert that the 1D psi profile goes in the ``expected`` direction.

    The grid is assumed to run from the magnetic axis outwards. Only the first and
    last points are compared, so a grid that does not start on the axis (e.g. in
    edge_profiles) gives the same result, as long as psi is monotonic.
    """
    if psi is None or len(psi) < 2:
        return
    check_psi_direction(psi[0], psi[-1], expected, msg)


def psi_messages(cocos, sigma_bp, scalars, profile, ip_ref):
    """Return the messages of the psi direction checks from the axis and boundary
    values (``scalars``) and from the ``profile``."""
    sign = "" if sigma_bp > 0 else "-"
    return (
        f"COCOS {cocos}: {scalars} must have the sign of {sign}{ip_ref}",
        f"COCOS {cocos}: {profile} (last - first point) must have the sign of "
        f"{sign}{ip_ref}",
    )


def check_current_density(profiles_1d, sign_ip, cocos, ip_ref="Ip"):
    """Assert that the average toroidal current density has the sign of Ip."""
    if sign_ip is None:
        return
    for name in ["j_phi", "j_tor"]:
        j = get_field(profiles_1d, name)
        if j is not None:
            sign_j = mean_sign(j)
            if sign_j is not None:
                assert (
                    sign_j == sign_ip
                ), f"COCOS {cocos}: average {name} must have the sign of {ip_ref}"
            return


def check_equilibrium(ids, cocos):
    """Check the COCOS sign relations of an equilibrium IDS."""
    sigma_bp = COCOS[cocos]["sigma_bp"]
    sigma_rtp = COCOS[cocos]["sigma_rhothetaphi"]
    b0 = get_field(ids, "vacuum_toroidal_field/b0")
    msg_psi_global, msg_psi_profile = psi_messages(
        cocos,
        sigma_bp,
        "global_quantities psi_boundary - psi_axis",
        "profiles_1d/psi",
        "Ip",
    )

    for itime, time_slice in enumerate(ids.time_slice):
        time = slice_time(ids, ids.time_slice, itime)
        sign_b0 = reference_sign(value_at(ids, b0, itime, time))
        sign_ip = reference_sign(get_field(time_slice, "global_quantities/ip"))
        gq = time_slice.global_quantities
        p1d = time_slice.profiles_1d

        if sign_b0 is not None:
            check_sign(
                get_field(p1d, "f"),
                sign_b0,
                f"COCOS {cocos}: F = R*B_phi must have the sign of B0",
            )
            # phi is zero on the magnetic axis (checked in equilibrium.py)
            phi = get_field(p1d, "phi")
            if phi is not None:
                check_sign(
                    phi[1:],
                    sign_b0,
                    f"COCOS {cocos}: toroidal flux phi must have the sign of B0",
                )

        if sign_ip is None:
            continue

        expected_psi = sigma_bp * sign_ip
        check_psi_direction(
            get_field(gq, "psi_axis"),
            get_field(gq, "psi_boundary"),
            expected_psi,
            msg_psi_global,
        )
        check_psi_profile(get_field(p1d, "psi"), expected_psi, msg_psi_profile)
        check_current_density(p1d, sign_ip, cocos)

        if sign_b0 is None:
            continue

        expected_q = sigma_rtp * sign_ip * sign_b0
        msg_q = f"COCOS {cocos}: q must have the sign of Ip*B0"
        for path in ["q_axis", "q_95", "q_min/value"]:
            check_sign(get_field(gq, path), expected_q, msg_q)
        check_sign(get_field(p1d, "q"), expected_q, msg_q)


def check_profiles(ids, cocos):
    """Check the COCOS sign relations of a core_profiles-like IDS
    (core_profiles, edge_profiles, plasma_profiles).

    When the IDS has no plasma current (edge_profiles), the sign of Ip is inferred
    from the q profile and B0. The psi and current density checks then verify
    the COCOS relations between psi, j, q and B0, which do not depend on Ip.
    """
    sigma_bp = COCOS[cocos]["sigma_bp"]
    sigma_rtp = COCOS[cocos]["sigma_rhothetaphi"]
    b0 = get_field(ids, "vacuum_toroidal_field/b0")
    ip = get_field(ids, "global_quantities/ip")

    for itime, profiles_1d in enumerate(ids.profiles_1d):
        time = slice_time(ids, ids.profiles_1d, itime)
        sign_b0 = reference_sign(value_at(ids, b0, itime, time))
        sign_ip = reference_sign(value_at(ids, ip, itime, time))
        ip_ref = "Ip"
        q = get_field(profiles_1d, "q")

        if sign_ip is not None and sign_b0 is not None:
            check_sign(
                q,
                sigma_rtp * sign_ip * sign_b0,
                f"COCOS {cocos}: q must have the sign of Ip*B0",
            )
        elif q is not None and sign_b0 is not None:
            # Infer the sign of Ip from q, provided that q has a single sign
            sign_q = mean_sign(q)
            if sign_q is not None:
                check_sign(
                    q,
                    sign_q,
                    "q must not change sign along the profile "
                    "(needed to infer the sign of Ip)",
                )
                sign_ip = sigma_rtp * sign_q * sign_b0
                ip_ref = "Ip (inferred from q*B0)"

        if sign_ip is None:
            continue

        expected_psi = sigma_bp * sign_ip
        msg_psi_grid, msg_psi_profile = psi_messages(
            cocos,
            sigma_bp,
            "grid/psi_boundary - grid/psi_magnetic_axis",
            "grid/psi",
            ip_ref,
        )
        grid = profiles_1d.grid
        check_psi_direction(
            get_field(grid, "psi_magnetic_axis"),
            get_field(grid, "psi_boundary"),
            expected_psi,
            msg_psi_grid,
        )
        check_psi_profile(get_field(grid, "psi"), expected_psi, msg_psi_profile)
        check_current_density(profiles_1d, sign_ip, cocos, ip_ref)


def check_summary(ids, cocos):
    """Check the COCOS sign relations of a summary IDS.

    ip, b0 and q share the time coordinate, so they have the same length in data
    that follows the Data Dictionary. Inconsistent lengths are skipped.
    """
    sigma_rtp = COCOS[cocos]["sigma_rhothetaphi"]
    ip = get_field(ids, "global_quantities/ip/value")
    b0 = get_field(ids, "global_quantities/b0/value")
    if ip is None or b0 is None or len(ip) != len(b0):
        return
    expected_q = sigma_rtp * np.sign(ip) * np.sign(b0)
    unknown = np.logical_or(missing(ip), missing(b0))
    for path in ["global_quantities/q_95/value", "local/magnetic_axis/q/value"]:
        q = get_field(ids, path)
        if q is None or len(q) != len(ip):
            continue
        ignored = np.logical_or(
            np.logical_or(q == 0, missing(q)),
            np.logical_or(expected_q == 0, unknown),
        )
        assert np.logical_or(
            ignored, np.sign(q) == expected_q
        ), f"COCOS {cocos}: {path} must have the sign of Ip*B0"


@validator("equilibrium", version=DD3, lazy=True)
def validate_cocos11_equilibrium(ids):
    """Validate COCOS 11 sign conventions (DD3) in the EQUILIBRIUM IDS:
    q, psi, F, phi and j_tor against the signs of Ip and B0"""
    check_equilibrium(ids, 11)


@validator("equilibrium", version=DD4, lazy=True)
def validate_cocos17_equilibrium(ids):
    """Validate COCOS 17 sign conventions (DD4) in the EQUILIBRIUM IDS:
    q, psi, F, phi and j_phi against the signs of Ip and B0"""
    check_equilibrium(ids, 17)


@validator("core_profiles", version=DD3, lazy=True)
def validate_cocos11_core_profiles(ids):
    """Validate COCOS 11 sign conventions (DD3) in the CORE_PROFILES IDS:
    q, psi and j_tor against the signs of Ip and B0"""
    check_profiles(ids, 11)


@validator("core_profiles", version=DD4, lazy=True)
def validate_cocos17_core_profiles(ids):
    """Validate COCOS 17 sign conventions (DD4) in the CORE_PROFILES IDS:
    q, psi and j_phi against the signs of Ip and B0"""
    check_profiles(ids, 17)


@validator("edge_profiles", version=DD3, lazy=True)
def validate_cocos11_edge_profiles(ids):
    """Validate COCOS 11 sign conventions (DD3) in the EDGE_PROFILES IDS:
    psi direction and j_tor against the sign of Ip inferred from q and B0
    (q must have a single sign)"""
    check_profiles(ids, 11)


@validator("edge_profiles", version=DD4, lazy=True)
def validate_cocos17_edge_profiles(ids):
    """Validate COCOS 17 sign conventions (DD4) in the EDGE_PROFILES IDS:
    psi direction and j_phi against the sign of Ip inferred from q and B0
    (q must have a single sign)"""
    check_profiles(ids, 17)


@validator("plasma_profiles", version=DD4, lazy=True)
def validate_cocos17_plasma_profiles(ids):
    """Validate COCOS 17 sign conventions (DD4) in the PLASMA_PROFILES IDS:
    q, psi and j_phi against the signs of Ip and B0"""
    check_profiles(ids, 17)


@validator("summary", version=DD3, lazy=True)
def validate_cocos11_summary(ids):
    """Validate COCOS 11 sign conventions (DD3) in the SUMMARY IDS:
    q_95 and q on axis against the signs of Ip and B0"""
    check_summary(ids, 11)


@validator("summary", version=DD4, lazy=True)
def validate_cocos17_summary(ids):
    """Validate COCOS 17 sign conventions (DD4) in the SUMMARY IDS:
    q_95 and q on axis against the signs of Ip and B0"""
    check_summary(ids, 17)
