"""Required fields of EFIT++ in the pf_passive IDS"""

@validator("pf_passive")
def validate_required_fields(ids):
    """Validate that the pf_passive IDS has required fields."""

    homogeneous_time = ids.ids_properties.homogeneous_time

    # Axisymmetric passive conductors
    for loop in ids.loop:
        # machine description
        assert loop.name.has_value
        for element in loop.element:
            assert element.geometry.geometry_type in [2, 3, 5, 6]
            assert element.turns_with_sign.has_value
        # data
        assert loop.current.has_value
        assert loop.current_error_upper.has_value
        if homogeneous_time == 0:
            assert loop.time.has_value
