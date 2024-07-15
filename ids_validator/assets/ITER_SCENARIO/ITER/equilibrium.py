# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("equilibrium")
def validate_mandatory_values(ids):
    """Validate if the property exists by using has_value method in IMASPy."""

    # time_slice
    assert ids.time_slice.has_value
    for time_slice in ids.time_slice:

        # time_slice[:].global_quantities.ip
        assert time_slice.global_quantities.ip.has_value

        # time_slice[:].profiles_2d
        assert time_slice.profiles_2d.has_value
        for profiles_2d in time_slice.profiles_2d:

            assert profiles_2d.phi.has_value
            assert profiles_2d.psi.has_value
            assert profiles_2d.r.has_value
            assert profiles_2d.z.has_value

    # vacuum_toroidal_field.r0
    assert ids.vacuum_toroidal_field.r0.has_value

    # vacuum_toroidal_field.b0[:]
    assert ids.vacuum_toroidal_field.b0.has_value


@validator("equilibrium")
def validate_global_quantities_ip(ids):
    """Validate that time_slice(:)/global_quantities/ip is -17MA < ip <= 0."""

    for time_slice in ids.time_slice:
        assert -17000000.0 < time_slice.global_quantities.ip <= 0.0


@validator("equilibrium")
def validate_vacuum_toroidal_field_b0(ids):
    """Validate that vacuum_toroidal_field/b0(:) is b0 < 0."""

    assert ids.vacuum_toroidal_field.b0 < 0.0
