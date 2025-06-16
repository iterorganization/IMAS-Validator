"""Validation rules of ITER scenario database for the ``equlibrium`` IDS."""

@validator("equilibrium")
def validate_mandatory_values(ids):
    """Validate that mandatory quantities are provided."""

    # time_slice
    assert ids.time_slice.has_value
    for time_slice in ids.time_slice:

        # time_slice[:].global_quantities
        assert time_slice.global_quantities.ip.has_value

        # time_slice[:].profiles_2d
        assert time_slice.profiles_2d.has_value
        for profiles_2d in time_slice.profiles_2d:

            assert profiles_2d.psi.has_value
            assert profiles_2d.r.has_value
            assert profiles_2d.z.has_value

    # vacuum_toroidal_field.r0
    assert ids.vacuum_toroidal_field.r0.has_value

    # vacuum_toroidal_field.b0[:]
    assert ids.vacuum_toroidal_field.b0.has_value


@validator("equilibrium")
def validate_cocos(ids):
    """Validate that fields are provided and computed COCOS agrees with the one in DD."""
    from idstools.cocos import IDS_COCOS, compute_COCOS

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
                # ids._obj instead of ids since '&' operator is not supported yet.
                cocos = compute_COCOS(ids._obj, itime, i1)["COCOS"]
            except Exception as e:
                cocos = None

            assert (
                IDS_COCOS == cocos
            ), f"COCOS mismatch for time_slice {itime}, profiles_2d {i1}, Expected/Computed: {IDS_COCOS}/{cocos}"
