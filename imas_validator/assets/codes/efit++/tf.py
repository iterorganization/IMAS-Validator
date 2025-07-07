"""Required fields of EFIT++ in the tf IDS"""

@validator("tf")
def validate_required_fields(ids):
    """Validate that the tf IDS has required fields."""

    homogeneous_time = ids.ids_properties.homogeneous_time

    # Vacuume field times major radius in the toroidal field magnet.
    # b_field_tor_vacuum_r is obsolete.
    assert ids.b_field_phi_vacuum_r.data.has_value
    if homogeneous_time == 0:
        assert ids.b_field_phi_vacuum_r.time.has_value
