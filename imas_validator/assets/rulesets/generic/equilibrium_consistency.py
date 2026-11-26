"""Generic rules checking that the profiles of an equilibrium IDS are consistent with
each other and with the 2D equilibrium.

A Grad-Shafranov solver produces psi(R,Z) from dpressure_dpsi and f_df_dpsi. The
other profiles_1d quantities follow from these and the flux surfaces:

- pressure = pressure(boundary) + int dpressure_dpsi dpsi
- f**2 = f(boundary)**2 + 2 int f_df_dpsi dpsi
- q = dphi/dpsi (magnitudes; the signs are checked in cocos.py)
- rho_tor_norm = sqrt(phi / phi(boundary))
- global_quantities/q_95 and q_axis are q at psi_norm = 0.95 and on axis
- int j_tor darea = ip
- profiles_1d/psi lies between psi_axis and psi_boundary
- psi_axis and psi_boundary are the values of the 2D psi map at the magnetic axis
  and on the boundary outline
- the volume enclosed by a flux surface is that of the 2D psi map

Codes that write profiles taken from elsewhere (for example from a transport solver)
fail these checks even though each profile looks reasonable on its own.

When the checks apply:

- Time slices without an equilibrium (psi_axis equal to psi_boundary, or |ip|
  below IP_MIN) are skipped, and so are checks whose inputs are not filled.
- NaN or fill values at the ends of the profiles (for example q on the
  separatrix) are left out; profiles with such values inside are skipped.
  Profiles stored from the boundary to the axis are reversed.
- Checks over the whole plasma (rho_tor_norm, int j_tor darea) need a
  profiles_1d grid from the magnetic axis to the boundary. Other checks use the
  range covered by profiles_1d.
- The integrals and derivatives along profiles_1d allow for their leading
  truncation error, h**3 |y''| / 12 per interval for the trapezoidal rule. The
  estimate assumes the profiles are resolved by their grid: a pedestal narrower
  than the grid spacing can fail although the profiles are consistent.
- The checks against the 2D map need a rectangular profiles_2d grid that covers
  the points compared, with valid values inside the boundary, are done on at most
  MAX_2D_SLICES time slices per IDS, and allow for the bilinear interpolation
  error of the map, estimated from its second differences: a coarse map gets a
  correspondingly wider tolerance.
"""

import numpy as np
from imas.ids_defs import EMPTY_FLOAT

# Tolerances, relative to the largest magnitude of the compared quantity
RTOL_INTEGRAL = 1e-2  # pressure, f**2
RTOL_Q = 2e-2  # q vs dphi/dpsi (numerical derivative)
ATOL_RHO = 5e-3  # rho_tor_norm vs sqrt(phi/phi_boundary)
RTOL_Q_GLOBAL = 1e-2  # q_95, q_axis
RTOL_IP = 1e-2  # int j_tor darea vs ip
RTOL_PSI_2D = 1e-2  # 2D psi at axis / boundary, relative to |psi_boundary - psi_axis|
RTOL_GEOMETRY_2D = 1e-2  # volume from the 2D map, plus the map's own error
# Settings of the checks
IP_MIN = 1e3  # [A] slices with a smaller |ip| are skipped
ATOL_PSI_NORM_ENDS = 1e-3  # psi_norm within this of 0 / 1 counts as axis / boundary
PSI_NORM_INTERIOR = (0.05, 0.95)  # range of psi_norm for q vs dphi/dpsi
MAX_SPACING_Q95 = 0.03  # q_95 is checked only on finer grids around psi_norm = 0.95
PSI_NORM_2D = (0.3, 0.5, 0.7, 0.9)  # flux surfaces compared with the 2D map
REFINE_2D = 4  # refinement of the 2D grid for the volume integral
MAX_2D_SLICES = 20


def raw(wrapped):
    """Return the numbers in a wrapped IDS node or result as a float array."""
    obj = wrapped._obj
    return np.asarray(getattr(obj, "value", obj), dtype=float)


def filled(*nodes):
    return all(node is not None and node.has_value for node in nodes)


def cumulative_integral(y, x):
    """Trapezoidal cumulative integral of y(x), starting at zero."""
    return np.insert(np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x)), 0, 0.0)


def profile_curvature(values, grid):
    """Second derivative at the interior profile points."""
    return 2 * np.diff(np.diff(values) / np.diff(grid)) / (grid[2:] - grid[:-2])


def trapezoid_error(y, x):
    """Leading truncation error of cumulative_integral(y, x) accumulated from the
    last point: sum of h**3 |y''| / 12 over the intervals between each point and
    the edge (y'' from second differences, extended to the end intervals)."""
    y, x = raw(y), raw(x)
    curvature = np.abs(profile_curvature(y, x))
    at_points = np.concatenate([curvature[:1], curvature, curvature[-1:]])
    per_interval = np.diff(x) ** 3 * 0.5 * (at_points[1:] + at_points[:-1]) / 12
    return np.abs(np.insert(np.cumsum(per_interval[::-1]), 0, 0.0)[::-1])


def valid(values):
    """Return where ``values`` are finite and not the IMAS fill value."""
    return np.isfinite(values) & ~np.isclose(values, EMPTY_FLOAT)


def equilibrium_slices(ids):
    """Yield (time_slice, psi_axis, psi_boundary) for the time slices that hold an
    equilibrium: |ip| >= IP_MIN and psi_boundary different from psi_axis."""
    for time_slice in ids.time_slice:
        gq = time_slice.global_quantities
        if not filled(gq.psi_axis, gq.psi_boundary, gq.ip):
            continue
        psi_axis, psi_boundary = float(raw(gq.psi_axis)), float(raw(gq.psi_boundary))
        ip = float(raw(gq.ip))
        if not valid(np.array([psi_axis, psi_boundary, ip])).all() or abs(ip) < IP_MIN:
            continue
        span = psi_boundary - psi_axis
        if not np.isfinite(span) or abs(span) <= 1e-9 * max(abs(psi_axis), 1.0):
            continue
        yield time_slice, psi_axis, psi_boundary


def profile_slices(ids, *names):
    """Yield (time_slice, psi, psi_norm, profiles) for the equilibrium slices where
    profiles_1d/psi and the profiles ``names`` are filled on the same grid, ordered
    with psi_norm increasing (profiles stored from the boundary to the axis are
    reversed). Points at either end where a value is NaN or the fill value are
    left out; slices with such points inside, fewer than 4 valid points or a psi
    grid that is not monotonic are skipped."""
    for time_slice, psi_axis, psi_boundary in equilibrium_slices(ids):
        p1 = time_slice.profiles_1d
        if not filled(p1.psi) or not all(hasattr(p1._obj, n) for n in names):
            continue
        profiles = [getattr(p1, name) for name in names]
        if not filled(*profiles):
            continue
        n = len(raw(p1.psi))
        if any(len(raw(profile)) != n for profile in profiles):
            continue
        ok = np.all([valid(raw(node)) for node in [p1.psi, *profiles]], axis=0)
        index = np.flatnonzero(ok)
        if len(index) < 4 or not ok[index[0] : index[-1] + 1].all():
            continue
        keep = slice(index[0], index[-1] + 1)
        step = np.diff((raw(p1.psi)[keep] - psi_axis) / (psi_boundary - psi_axis))
        if np.all(step < 0):
            keep = slice(index[-1], index[0] - 1 if index[0] > 0 else None, -1)
        elif not np.all(step > 0):
            continue
        psi = p1.psi[keep]
        psi_norm = (psi - psi_axis) / (psi_boundary - psi_axis)
        yield time_slice, psi, psi_norm, [profile[keep] for profile in profiles]


def from_axis_to_boundary(psi_norm):
    values = raw(psi_norm)
    return (
        abs(values[0]) <= ATOL_PSI_NORM_ENDS
        and abs(values[-1] - 1) <= ATOL_PSI_NORM_ENDS
    )


@validator("equilibrium")
def validate_pressure_consistency(ids):
    """Validate that profiles_1d/pressure equals the pressure at the edge of the
    profile plus the integral of profiles_1d/dpressure_dpsi over psi in the
    EQUILIBRIUM IDS"""
    for _, psi, _, (p, dp) in profile_slices(ids, "pressure", "dpressure_dpsi"):
        integral = cumulative_integral(dp, psi)
        expected = p[-1] + integral - integral[-1]
        scale = max(np.max(np.abs(raw(p))), np.max(np.abs(raw(expected))))
        error = np.max(np.abs(raw(p) - raw(expected))) / scale if scale > 0 else 0.0
        atol = RTOL_INTEGRAL * scale + trapezoid_error(dp, psi)
        assert Approx(
            p, expected, rtol=0, atol=atol
        ), f"pressure differs from int dpressure_dpsi dpsi by {error:.1%} of max(p)"


@validator("equilibrium")
def validate_f_consistency(ids):
    """Validate that profiles_1d/f**2 equals its value at the edge of the profile
    plus twice the integral of profiles_1d/f_df_dpsi over psi in the EQUILIBRIUM
    IDS"""
    for _, psi, _, (f, ffp) in profile_slices(ids, "f", "f_df_dpsi"):
        integral = 2 * cumulative_integral(ffp, psi)
        expected = integral - integral[-1]  # f**2 - f(edge)**2
        written = f * f - f[-1] * f[-1]
        # f**2 - f_edge**2 is small compared with f**2; compare the variation itself,
        # with a floor of 1e-4 f_edge**2 for nearly vacuum-field profiles
        f_edge = raw(f)[-1]
        scale = max(
            np.max(np.abs(raw(expected))),
            np.max(np.abs(raw(written))),
            1e-4 * f_edge**2,
        )
        if scale == 0:
            continue
        error = np.max(np.abs(raw(written) - raw(expected))) / scale
        atol = RTOL_INTEGRAL * scale + 2 * trapezoid_error(ffp, psi)
        assert Approx(
            written, expected, rtol=0, atol=atol
        ), f"f**2 differs from 2 int f_df_dpsi dpsi by {error:.1%} of its variation"


@validator("equilibrium")
def validate_q_phi_consistency(ids):
    """Validate that |profiles_1d/q| equals |dphi/dpsi| inside the plasma in the
    EQUILIBRIUM IDS"""
    for _, psi, psi_norm, (q, phi) in profile_slices(ids, "q", "phi"):
        values = raw(psi_norm)
        inner = (values > PSI_NORM_INTERIOR[0]) & (values < PSI_NORM_INTERIOR[1])
        inner[[0, -1]] = False
        if np.count_nonzero(inner) < 2:
            continue
        expected = np.abs(np.gradient(phi, psi))[inner]
        written = np.abs(q[inner])
        scale = np.max(raw(written))
        # The three-point derivative of phi has leading error h_left*h_right*q''/6.
        h = np.diff(values)
        curvature = profile_curvature(raw(q), values)
        truncation = (np.abs(curvature) * h[1:] * h[:-1] / 6)[inner[1:-1]]
        error = np.max(np.abs(raw(written) - raw(expected))) / scale if scale else 0
        assert Approx(
            written, expected, rtol=0, atol=RTOL_Q * scale + truncation
        ), f"|q| differs from |dphi/dpsi| by {error:.1%} of max|q|"


@validator("equilibrium")
def validate_rho_tor_norm_consistency(ids):
    """Validate that profiles_1d/rho_tor_norm equals sqrt(phi/phi(boundary)) when
    profiles_1d reaches the boundary in the EQUILIBRIUM IDS"""
    for _, _, psi_norm, (rho, phi) in profile_slices(ids, "rho_tor_norm", "phi"):
        if not from_axis_to_boundary(psi_norm) or raw(phi)[-1] == 0:
            continue
        expected = np.sqrt(np.abs(phi / phi[-1]))
        error = np.max(np.abs(raw(rho) - raw(expected)))
        assert Approx(
            rho, expected, rtol=0, atol=ATOL_RHO
        ), f"rho_tor_norm differs from sqrt(phi/phi_boundary) by up to {error:.3f}"


@validator("equilibrium")
def validate_q_global_consistency(ids):
    """Validate that |global_quantities/q_95| and |q_axis| equal the q profile at
    psi_norm = 0.95 and on axis in the EQUILIBRIUM IDS (signs are checked in
    cocos.py)"""
    for time_slice, _, psi_norm, (q,) in profile_slices(ids, "q"):
        gq = time_slice.global_quantities
        values = raw(psi_norm)
        i = int(np.clip(np.searchsorted(values, 0.95), 1, len(values) - 1))
        if (
            filled(gq.q_95)
            and valid(raw(gq.q_95))
            and values[0] <= 0.95 <= values[-1]
            and values[i] - values[i - 1] <= MAX_SPACING_Q95
        ):
            expected = np.abs(np.interp(0.95, psi_norm, q))
            curvature = profile_curvature(raw(q), values)
            q_second = np.interp(0.95, values[1:-1], curvature)
            truncation = abs(q_second) * (0.95 - values[i - 1]) * (values[i] - 0.95) / 2
            assert Approx(
                np.abs(gq.q_95), expected, rtol=RTOL_Q_GLOBAL, atol=truncation
            ), (
                f"|q_95| = {abs(float(raw(gq.q_95))):.4g} "
                f"but |q(psi_norm=0.95)| = {float(raw(expected)):.4g}"
            )
        if (
            filled(gq.q_axis)
            and valid(raw(gq.q_axis))
            and abs(values[0]) <= ATOL_PSI_NORM_ENDS
        ):
            assert Approx(np.abs(gq.q_axis), np.abs(q[0]), rtol=RTOL_Q_GLOBAL), (
                f"|q_axis| = {abs(float(raw(gq.q_axis))):.4g} "
                f"differs from |q| on axis = {abs(raw(q)[0]):.4g}"
            )


@validator("equilibrium")
def validate_j_tor_ip_consistency(ids):
    """Validate that the toroidal current density profile integrated over the
    poloidal cross-section equals global_quantities/ip, when profiles_1d covers
    the whole plasma, in the EQUILIBRIUM IDS"""
    # DD4 renamed j_tor to j_phi; some DD3 versions have both, with only one filled
    name = "j_tor"
    for time_slice in ids.time_slice:
        if hasattr(time_slice.profiles_1d._obj, "j_phi"):
            if time_slice.profiles_1d._obj.j_phi.has_value:
                name = "j_phi"
                break
            if not hasattr(time_slice.profiles_1d._obj, "j_tor"):
                name = "j_phi"
    for time_slice, _, psi_norm, (j, area) in profile_slices(ids, name, "area"):
        if not from_axis_to_boundary(psi_norm):
            continue
        ip = time_slice.global_quantities.ip
        ip_profile = np.sum(0.5 * (j[1:] + j[:-1]) * np.diff(area))
        ip_value, ip_integral = float(raw(ip)), float(raw(ip_profile))
        error = abs(ip_integral - ip_value) / abs(ip_value)
        atol = float(trapezoid_error(j, area)[0])
        assert Approx(
            ip, ip_profile, rtol=RTOL_IP, atol=atol
        ), f"int j darea = {ip_integral:.4g} A differs from ip by {error:.1%}"


@validator("equilibrium")
def validate_psi_range_consistency(ids):
    """Validate that profiles_1d/psi lies between global_quantities/psi_axis and
    psi_boundary, so that both use the same flux (same offset, factor 2 pi), in
    the EQUILIBRIUM IDS"""
    for _, psi, psi_norm, _ in profile_slices(ids):
        low, high = float(np.min(raw(psi_norm))), float(np.max(raw(psi_norm)))
        assert Approx(
            np.clip(psi_norm, -ATOL_PSI_NORM_ENDS, 1 + ATOL_PSI_NORM_ENDS), psi_norm
        ), (
            f"profiles_1d/psi spans psi_norm = {low:.4g}..{high:.4g}, "
            "outside psi_axis..psi_boundary"
        )


def rectangular_psi(time_slice):
    """Return (r, z, psi, psi_values) of the first rectangular profiles_2d grid, with
    r and z increasing, or None. ``psi`` is the wrapped node (reordered to match r
    and z), ``psi_values`` its numbers with NaN in place of invalid values."""
    for p2 in time_slice.profiles_2d:
        if not filled(p2.grid_type.index) or int(raw(p2.grid_type.index)) != 1:
            continue
        if not filled(p2.grid.dim1, p2.grid.dim2, p2.psi):
            continue
        r, z, psi = raw(p2.grid.dim1), raw(p2.grid.dim2), p2.psi
        if len(r) < 3 or len(z) < 3 or raw(psi).shape != (len(r), len(z)):
            continue
        if np.all(np.diff(r) < 0):
            r, psi = r[::-1], psi[::-1, :]
        if np.all(np.diff(z) < 0):
            z, psi = z[::-1], psi[:, ::-1]
        if not (np.all(np.diff(r) > 0) and np.all(np.diff(z) > 0)):
            continue
        values = raw(psi)
        return r, z, psi, np.where(valid(values), values, np.nan)
    return None


def interpolation_error(psi, inside):
    """Bound on the bilinear interpolation error of the psi map in the points
    ``inside`` (boolean mask on the grid): (|d2psi_r| + |d2psi_z|)/8 from the
    second differences, which equals h_r**2 |psi_rr|/8 + h_z**2 |psi_zz|/8."""
    d2 = np.zeros_like(psi)
    d2[1:-1, :] += np.abs(psi[2:, :] - 2 * psi[1:-1, :] + psi[:-2, :])
    d2[:, 1:-1] += np.abs(psi[:, 2:] - 2 * psi[:, 1:-1] + psi[:, :-2])
    d2 = d2[inside & np.isfinite(d2)]
    return np.max(d2) / 8 if d2.size else 0.0


def interpolate_2d(r, z, f, rq, zq):
    """Bilinear interpolation of f(r, z) at the points (rq, zq); r, z increasing.
    ``f`` can be a wrapped node, which then stays in the result."""
    i = np.clip(np.searchsorted(r, rq) - 1, 0, len(r) - 2)
    j = np.clip(np.searchsorted(z, zq) - 1, 0, len(z) - 2)
    tr = (rq - r[i]) / (r[i + 1] - r[i])
    tz = (zq - z[j]) / (z[j + 1] - z[j])
    return (
        f[i, j] * ((1 - tr) * (1 - tz))
        + f[i + 1, j] * (tr * (1 - tz))
        + f[i, j + 1] * ((1 - tr) * tz)
        + f[i + 1, j + 1] * (tr * tz)
    )


def inside_polygon(px, py, vx, vy):
    """Return where the points (px, py) lie inside the polygon (vx, vy); only the
    points inside its bounding box are tested."""
    box = (px >= np.min(vx)) & (px <= np.max(vx)) & (py >= np.min(vy))
    box &= py <= np.max(vy)
    result = np.zeros(px.shape, dtype=bool)
    result[box] = points_inside_polygon(px[box], py[box], vx, vy)
    return result


def points_inside_polygon(px, py, vx, vy):
    """Even-odd ray casting for the points (px, py) and the polygon (vx, vy)."""
    inside = np.zeros(px.shape, dtype=bool)
    j = len(vx) - 1
    for i in range(len(vx)):
        crosses = (vy[i] > py) != (vy[j] > py)
        with np.errstate(divide="ignore", invalid="ignore"):
            x_cross = (vx[j] - vx[i]) * (py - vy[i]) / (vy[j] - vy[i]) + vx[i]
        inside ^= crosses & (px < x_cross)
        j = i
    return inside


def covers(r, z, rq, zq):
    """Return whether all points (rq, zq) lie on the rectangular grid (r, z)."""
    rq, zq = np.asarray(rq), np.asarray(zq)
    return bool(np.all((rq >= r[0]) & (rq <= r[-1]) & (zq >= z[0]) & (zq <= z[-1])))


def boundary_outline(time_slice):
    outline = time_slice.boundary.outline
    if not filled(outline.r, outline.z):
        return None
    b_r, b_z = raw(outline.r), raw(outline.z)
    if len(b_r) != len(b_z) or len(b_r) < 3:
        return None
    return b_r, b_z


def sampled(slices):
    """Return at most MAX_2D_SLICES evenly spaced elements of ``slices``."""
    if len(slices) <= MAX_2D_SLICES:
        return slices
    index = np.unique(np.linspace(0, len(slices) - 1, MAX_2D_SLICES).astype(int))
    return [slices[i] for i in index]


@validator("equilibrium")
def validate_psi_2d_consistency(ids):
    """Validate that the 2D psi map equals global_quantities/psi_axis at the
    magnetic axis and psi_boundary on the boundary outline in the EQUILIBRIUM
    IDS"""
    candidates = [
        (time_slice, psi_axis, psi_boundary, grid)
        for time_slice, psi_axis, psi_boundary in equilibrium_slices(ids)
        for grid in [rectangular_psi(time_slice)]
        if grid is not None
    ]
    for time_slice, psi_axis, psi_boundary, grid in sampled(candidates):
        r, z, psi, psi_values = grid
        gq = time_slice.global_quantities
        span = abs(psi_boundary - psi_axis)
        outline = boundary_outline(time_slice)
        if outline is not None and not covers(r, z, *outline):
            outline = None
        rr, zz = np.meshgrid(r, z, indexing="ij")
        inside = (
            inside_polygon(rr, zz, *outline)
            if outline is not None
            else np.ones(rr.shape, dtype=bool)
        )
        atol = RTOL_PSI_2D * span + interpolation_error(psi_values, inside)
        if filled(gq.magnetic_axis.r, gq.magnetic_axis.z):
            r_axis, z_axis = raw(gq.magnetic_axis.r), raw(gq.magnetic_axis.z)
            finite = np.isfinite(interpolate_2d(r, z, psi_values, r_axis, z_axis))
            if covers(r, z, r_axis, z_axis) and finite:
                at_axis = interpolate_2d(r, z, psi, r_axis, z_axis)
                error = abs(float(raw(at_axis)) - psi_axis) / span
                assert Approx(
                    gq.psi_axis, at_axis, rtol=0, atol=atol
                ), f"2D psi at the axis differs from psi_axis by {error:.1%} of range"
        if outline is not None and np.all(
            np.isfinite(interpolate_2d(r, z, psi_values, *outline))
        ):
            on_boundary = interpolate_2d(r, z, psi, *outline)
            error = np.max(np.abs(raw(on_boundary) - psi_boundary)) / span
            assert Approx(
                gq.psi_boundary, on_boundary, rtol=0, atol=atol
            ), f"2D psi on the outline is off psi_boundary by {error:.1%} of range"


@validator("equilibrium")
def validate_geometry_2d_consistency(ids):
    """Validate that profiles_1d/volume equals the volume enclosed by the flux
    surfaces of the 2D psi map in the EQUILIBRIUM IDS"""
    equilibria = {id(s._obj): (a, b) for s, a, b in equilibrium_slices(ids)}
    candidates = []
    for time_slice, _, psi_norm, (volume,) in profile_slices(ids, "volume"):
        grid, outline = rectangular_psi(time_slice), boundary_outline(time_slice)
        if grid is None or outline is None or not covers(*grid[:2], *outline):
            continue
        r, z, _, psi_values = grid
        r0, z0 = np.meshgrid(r, z, indexing="ij")
        inside_0 = inside_polygon(r0, z0, *outline)
        # the map must be valid inside the plasma and on the cells around it
        near = inside_0.copy()
        near[1:, :] |= inside_0[:-1, :]
        near[:-1, :] |= inside_0[1:, :]
        near[:, 1:] |= near[:, :-1].copy()
        near[:, :-1] |= near[:, 1:].copy()
        if not np.all(np.isfinite(psi_values[near])):
            continue
        candidates.append((time_slice, psi_norm, volume, grid, outline, inside_0))
    for time_slice, psi_norm, volume, grid, outline, inside_0 in sampled(candidates):
        r, z, _, psi_values = grid
        psi_axis, psi_boundary = equilibria[id(time_slice._obj)]
        span = psi_boundary - psi_axis
        # the map is only known to within its interpolation error, which shifts a
        # flux surface by up to delta in psi_norm
        delta = interpolation_error(psi_values, inside_0) / abs(span)
        # bilinear refinement of the map: cell counting on the refined grid, only
        # where a compared flux surface can be
        r_fine = np.linspace(r[0], r[-1], (len(r) - 1) * REFINE_2D + 1)
        z_fine = np.linspace(z[0], z[-1], (len(z) - 1) * REFINE_2D + 1)
        rr, zz = np.meshgrid(r_fine, z_fine, indexing="ij")
        norm = (interpolate_2d(r, z, psi_values, rr, zz) - psi_axis) / span
        cell = (r_fine[1] - r_fine[0]) * (z_fine[1] - z_fine[0])
        candidate = np.nan_to_num(norm, nan=np.inf) <= max(PSI_NORM_2D)
        inside = np.zeros(rr.shape, dtype=bool)
        inside[candidate] = inside_polygon(rr[candidate], zz[candidate], *outline)
        values = raw(psi_norm)
        slope = np.gradient(raw(volume), values)
        for level in PSI_NORM_2D:
            if not values[0] <= level <= values[-1]:
                continue
            from_2d = 2 * np.pi * np.sum(rr[inside & (norm <= level)]) * cell
            at_level = np.interp(level, psi_norm, volume)
            atol = delta * abs(np.interp(level, values, slope))
            assert Approx(at_level, from_2d, rtol=RTOL_GEOMETRY_2D, atol=atol), (
                f"volume(psi_norm={level}): {float(raw(at_level)):.4g} (1D), "
                f"{from_2d:.4g} (2D)"
            )
