"""Required fields of EFIT++ in the pf_active IDS"""

@validator("pf_active")
def validate_required_fields(ids):
    """Validate that the pf_active IDS has required fields."""

    homogeneous_time = ids.ids_properties.homogeneous_time

    # Axisymmetric poloidal field coils
    for coil in ids.coil:
        # machine description
        assert coil.name.has_value
        assert coil.identifier.has_value
        for element in coil:
            assert element.geometry.geometry_type in [2, 3, 5, 6]
            assert element.turns_with_sign.has_value

        # data
        assert coil.current.data.has_value
        assert coil.current.data_error_upper.has_value
        if homogeneous_time == 0:
            assert coil.current.time.has_value

    # PF power supplies
    for supply in ids.supply:
        assert supply.name.has_value
        assert supply.identifier.has_value

    # Circuits
    for circuit in ids.scircuit:
        assert circuit.connections.has_value
