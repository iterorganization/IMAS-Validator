"""ITER-specific validation rules for the ``equlibrium`` IDS."""

@validator("equilibrium")
def validate_global_quantities_ip(ids):
    """Validate that time_slice(:)/global_quantities/ip is -17 MA <= ip <= 0 MA"""

    for time_slice in ids.time_slice:
        assert -17000000.0 <= time_slice.global_quantities.ip <= 0.0


@validator("equilibrium")
def validate_vacuum_toroidal_field_b0(ids):
    """Validate that vacuum_toroidal_field/b0(:) is -8 T < b0 < 0 T"""

    assert -8.0 <= ids.vacuum_toroidal_field.b0 <= 0.0
