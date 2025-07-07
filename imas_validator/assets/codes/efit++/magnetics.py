"""Required fields of EFIT++ in the magnetics IDS"""

@validator("magnetics")
def validate_required_fields(ids):
    """Validate that the magnetics IDS has required fields."""

    homogeneous_time = ids.ids_properties.homogeneous_time

    # Magnetic field probes
    for b_field_pol_probe in ids.b_field_pol_probe:
        # machine description
        assert b_field_pol_probe.name.has_value
        assert b_field_pol_probe.identifier.has_value
        assert b_field_pol_probe.position.r.has_value
        assert b_field_pol_probe.position.z.has_value
        assert b_field_pol_probe.position.phi.has_value
        assert b_field_pol_probe.poloidal_angle.has_value
        assert b_field_pol_probe.toroidal_angle.has_value
        assert b_field_pol_probe.area.has_value
        assert b_field_pol_probe.length.has_value
        assert b_field_pol_probe.turns.has_value
        # diagnostic data
        assert b_field_pol_probe.field.data.has_value
        assert b_field_pol_probe.field.data_error_upper.has_value
        if homogeneous_time == 0:
            assert b_field_pol_probe.field.time.has_value

    # Flux loops
    for flux_loop in ids.flux_loop:
        # machine description
        assert flux_loop.name.has_value
        assert flux_loop.identifier.has_value
        assert flux_loop.position.r.has_value
        assert flux_loop.position.z.has_value
        assert flux_loop.position.phi.has_value
        # diagnostic data
        assert flux_loop.flux.data.has_value
        assert flux_loop.flux.data_error_upper.has_value
        if homogeneous_time == 0:
            assert flux_loop.flux.time.has_value

    # Plasma current (reconstructed data)
    assert ids.ip.data.has_value
    assert ids.ip.data_error_upper.has_value
    if homogeneous_time == 0:
        assert ids.ip.time.has_value

    # Diamagnetic flux (reconstructed data)
    assert ids.diamagnetic_flux.data.has_value
    assert ids.diamagnetic_flux.data_error_upper.has_value
    if homogeneous_time == 0:
        assert ids.diamagnetic_flux.time.has_value
