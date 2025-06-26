"""Generic rules applying to the equilibrium IDS"""

import numpy as np


@validator("equilibrium", version="<4.0.0")
def validate_sign_DD3(ids):
    """
    Validate that the equilibrium IDS has consistent sign conventions.
    """

    # Loop through each time slice
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
            b0sign = np.sign(
                np.interp(time, ids.time, ids.vacuum_toroidal_field.b0)
            )
        else:
            b0sign = -9

        #
        # Validate the sign conventions for EM fields
        #

        if time_slice.profiles_1d.f.has_value:
            assert np.sign(time_slice.profiles_1d.f) == b0sign

        if time_slice.profiles_1d.phi.has_value:
            # phi at center found as zero in DINA, CORSICA and etc.
            assert np.sign(time_slice.profiles_1d.phi[1:]) == b0sign

        psi_axis = time_slice.global_quantities.psi_axis
        psi_boundary = time_slice.global_quantities.psi_boundary
        if psi_axis.has_value and psi_boundary.has_value:
            assert np.sign(psi_boundary - psi_axis) == ipsign

        if time_slice.global_quantities.q_95.has_value:
            assert np.sign(time_slice.global_quantities.q_95) == ipsign * b0sign


@validator("equilibrium", version=">=4.0.0")
def validate_sign(ids):
    """
    Validate that the equilibrium IDS has consistent sign conventions.
    """

    # Loop through each time slice
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
            b0sign = np.sign(
                np.interp(time, ids.time, ids.vacuum_toroidal_field.b0)
            )
        else:
            b0sign = -9

        #
        # Validate the sign conventions for EM fields
        #

        if time_slice.profiles_1d.f.has_value:
            assert np.sign(time_slice.profiles_1d.f) == b0sign

        if time_slice.profiles_1d.phi.has_value:
            # phi at center found as zero in DINA, CORSICA and etc.
            assert np.sign(time_slice.profiles_1d.phi[1:]) == b0sign

        psi_axis = time_slice.global_quantities.psi_axis
        psi_boundary = time_slice.global_quantities.psi_boundary
        if psi_axis.has_value and psi_boundary.has_value:
            assert np.sign(psi_boundary - psi_axis) == -ipsign

        if time_slice.global_quantities.q_95.has_value:
            assert np.sign(time_slice.global_quantities.q_95) == ipsign * b0sign
