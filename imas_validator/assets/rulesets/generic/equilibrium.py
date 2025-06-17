"""Generic rules applying to the equilibrium IDS"""
from imas_validator.common.cocos import IDS_COCOS, compute_COCOS

@validator("equilibrium")
def validate_cocos(ids):
    """
    Validate that COCOS computed corresponds to the one in DD.
    """

    # time_slice[:]
    for itime, time_slice in enumerate(ids.time_slice):

        # time_slice[:].profiles_2d
        for i1, profiles_2d in enumerate(time_slice.profiles_2d):

            if not (
                ids.vacuum_toroidal_field.b0.has_value
                and time_slice.global_quantities.ip.has_value
                and time_slice.global_quantities.magnetic_axis.z.has_value
                and time_slice.profiles_1d.psi.has_value
                and time_slice.profiles_1d.q.has_value
                and time_slice.profiles_1d.dpressure_dpsi.has_value
                and profiles_2d.b_field_z.has_value
                and profiles_2d.grid_type.index == 1
                and profiles_2d.psi.has_value
                and profiles_2d.r.has_value
            ):
                continue

            # Compute COCOS
            try:
                # ids._obj instead of ids since '&' operator not supported
                # yet in IMAS-Validator
                cocos = compute_COCOS(ids._obj, itime, i1)["COCOS"]
            except Exception:
                cocos = None

            assert IDS_COCOS == cocos, (
                f"COCOS mismatch for time_slice {itime}, profiles_2d {i1}, "
                f"Expected/Computed: {IDS_COCOS}/{cocos}"
            )
