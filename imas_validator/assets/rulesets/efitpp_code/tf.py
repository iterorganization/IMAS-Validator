"""Required fields of EFIT++ in the tf IDS"""

@validator("tf")
def validate_required_fields(ids):
    """Validate that the tf IDS has required fields."""

    # Vacuume field times major radius in the toroidal field magnet.
    assert ids.b_field_tor_vacuum_r.data.has_value
    assert ids.b_field_tor_vacuum_r.data.coordinates[0].has_value
