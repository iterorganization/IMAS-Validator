"""Generic rules applying to the equilibrium IDS"""

import numpy as np


def ip_b0_sign(ids):
    """
    Extract the sign of plasma current (Ip) and vacuum toroidal field (B0)
    for each time slice in an equilibrium IDS.

    This function determines the sign of the plasma current and toroidal
    magnetic field for each time slice, accounting for whether time is
    stored homogeneously or per slice. If a value is missing, a placeholder
    value of -9 is used.

    Parameters
    ----------
    ids : IDSWrapper
        An IMAS IDS object (typically 'equilibrium') containing time slice
        information, plasma current, and toroidal magnetic field data.

    Returns
    -------
    ipsigns : list of int
        List of signs of plasma current (`ip`) for each time slice.
        Values are typically -1, 0, or 1, or -9 if missing.
    b0signs : list of int
        List of signs of vacuum toroidal field (`b0`) interpolated at each
        time slice. Values are -1, 0, or 1, or -9 if missing.

    Notes
    -----
    - Uses `np.sign()` to determine the sign of scalar values.
    - Uses linear interpolation to match B0 values with time slices.
    - Placeholder `-9` indicates missing data.
    """

    # Initialize lists to store the signs of Ip and B0
    ipsigns = []
    b0signs = []

    for itime, time_slice in enumerate(ids.time_slice):
        # Get the time for this time slice
        if ids.ids_properties.homogeneous_time == 0:
            time = time_slice.time
        else:
            time = ids.time[itime]

        # Set sign of Ip
        if time_slice.global_quantities.ip.has_value:
            ipsign = np.sign(time_slice.global_quantities.ip)
        else:
            ipsign = -9

        # Set sign of B0
        if ids.vacuum_toroidal_field.b0.has_value:
            b0 = np.interp(time, ids.time, ids.vacuum_toroidal_field.b0)
            b0sign = np.sign(b0)
        else:
            b0sign = -9

        # Append the signs to the lists
        ipsigns.append(ipsign)
        b0signs.append(b0sign)

    return ipsigns, b0signs


@validator("equilibrium")
def validate_sign(ids):
    """
    Validate that the equilibrium IDS has consistent sign conventions.
    """

    # Get the sign of Ip and B0 for each time slice
    ipsigns, b0signs = ip_b0_sign(ids)

    # Set sigma_Bp for the version of the data dictionary
    ver = str(ids.ids_properties.version_put.data_dictionary.value)[0]
    if ver == "3":
        sigma_Bp = 1
    else:
        sigma_Bp = -1

    # Loop through each time slice
    for itime, time_slice in enumerate(ids.time_slice):

        # Set the sign of Ip and B0 for this time slice
        ipsign = ipsigns[itime]
        b0sign = b0signs[itime]

        #
        # Validate the sign conventions for EM fields
        #
        if time_slice.profiles_1d.f.has_value:
            assert np.sign(time_slice.profiles_1d.f) == b0sign

        if time_slice.profiles_1d.phi.has_value:
            assert Approx(time_slice.profiles_1d.phi[0], 0.0, atol=1e-2)
            assert np.sign(time_slice.profiles_1d.phi[1:]) == b0sign

        if time_slice.global_quantities.q_95.has_value:
            assert np.sign(time_slice.global_quantities.q_95) == ipsign * b0sign

        if time_slice.profiles_1d.pressure.has_value:
            assert np.sign(time_slice.profiles_1d.pressure) >= 0.0

        if time_slice.profiles_1d.f.has_value:
            assert np.sign(time_slice.profiles_1d.f) == b0sign

        psi_axis = time_slice.global_quantities.psi_axis
        psi_boundary = time_slice.global_quantities.psi_boundary
        psi_diff = psi_boundary - psi_axis
        if (
            psi_axis.has_value
            and psi_boundary.has_value
            # Avoid non-physical cases where psi_boundary == psi_axis
            and np.absolute(psi_diff) > 1e-6
        ):
            assert np.sign(psi_diff) == ipsign * sigma_Bp
