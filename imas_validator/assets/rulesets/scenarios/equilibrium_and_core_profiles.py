"""
Validation rules of ITER scenario database for the IDSes
``equlibrium`` and ``core_profiles``.
"""

import numpy as np


def get_samples(t1, f1, t2, f2, n=5):
    """
    Generate interpolated sample values from two time series for comparison.

    This function takes two time series (t1, f1) and (t2, f2), generates `n`
    random time points within the union of their time spans, and returns the
    interpolated values from both series at those sampled time points.

    Parameters
    ----------
    t1 : array_like
        Time array corresponding to the first data series `f1`.
        Must be 1D and sorted.
    f1 : array_like
        Value array corresponding to `t1`.
    t2 : array_like
        Time array corresponding to the second data series `f2`.
        Must be 1D and sorted.
    f2 : array_like
        Value array corresponding to `t2`.
    n : int, optional
        Number of sample points to generate (default is 5).

    Returns
    -------
    tuple of ndarray or bool
        A tuple (r1, r2), where:
            - r1 : interpolated values from `f1` at sampled time points
            - r2 : interpolated values from `f2` at the same time points
        If inputs are invalid (e.g. empty arrays), returns False.

    Notes
    -----
    - Uses linear interpolation (`np.interp`) for both series.
    - Returns False if either time or value array is empty.
    - Time sampling is done uniformly over the combined time span of t1 and t2.
    """

    if len(t1) == 0 or len(t2) == 0:
        return None

    tmin = min(t1[0], t2[0])
    tmax = max(t1[-1], t2[-1])

    if abs(tmax - tmin) < 1e-6:
        ts = [tmin]
    else:
        ts = (tmax - tmin) * np.random.random_sample((n,)) + tmin

    if len(f1) > 0 and len(f2) > 0:
        r1 = np.interp(ts, t1, f1)
        r2 = np.interp(ts, t2, f2)
        return (r1, r2)
    return None


@validator("equilibrium:0", "core_profiles:0")
def validate_inter_signal(eq, cp):
    """
    Validate that IDS fields in equilibrium and core_profiles match.
    """

    # ip check
    s = get_samples(
        eq.time_slice.coordinates[0],
        np.array([ts.global_quantities.ip for ts in eq.time_slice]),
        cp.global_quantities.ip.coordinates[0],
        cp.global_quantities.ip,
    )
    if s:
        Approx(s[0], s[1])

    # b0 check
    s = get_samples(
        eq.vacuum_toroidal_field.b0.coordinates[0],
        eq.vacuum_toroidal_field.b0,
        cp.vacuum_toroidal_field.b0.coordinates[0],
        cp.vacuum_toroidal_field.b0,
    )
    if s:
        Approx(s[0], s[1])
