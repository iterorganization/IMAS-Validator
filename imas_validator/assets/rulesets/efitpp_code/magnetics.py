"""Required fields of EFIT++ in the magnetics IDS"""

@validator("magnetics")
def validate_required_fields(ids):
    """Validate that the magnetics IDS has required fields."""

    # Magnetic field probes
    for b_field_pol_probe in ids.b_field_pol_probe:
        # machine description
        assert b_field_pol_probe.name.has_value
        assert b_field_pol_probe.identifier.has_value
        assert b_field_pol_probe.position.r.has_value
        assert b_field_pol_probe.position.z.has_value
        assert b_field_pol_probe.position.phi.has_value
        assert b_field_pol_probe.poloidal_angle.has_value
        # toroidal angle is not read by EFIT++?
        # assert b_field_pol_probe.toroidal_angle.has_value
        if b_field_pol_probe.type.index == 2:  # 'Mirnov probe'
            assert b_field_pol_probe.area.has_value
            assert b_field_pol_probe.length.has_value
            assert b_field_pol_probe.turns.has_value
        # diagnostic data
        assert b_field_pol_probe.field.data.has_value
        assert b_field_pol_probe.field.data_error_upper.has_value
        assert b_field_pol_probe.field.data.coordinates[0].has_value

    # Flux loops
    for flux_loop in ids.flux_loop:
        # machine description
        assert flux_loop.name.has_value
        assert flux_loop.identifier.has_value
        # position
        for position in flux_loop.position:
            assert position.r.has_value
            assert position.z.has_value
            assert position.phi.has_value
        # diagnostic data
        assert flux_loop.flux.data.has_value
        assert flux_loop.flux.data_error_upper.has_value
        assert flux_loop.flux.data.coordinates[0].has_value

    # Plasma current (reconstructed data)
    for ip in ids.ip:
        assert ip.data.has_value
        assert ip.data_error_upper.has_value
        assert ip.data.coordinates[0].has_value

    # Diamagnetic flux (reconstructed data)
    for diamagnetic_flux in ids.diamagnetic_flux:
        assert diamagnetic_flux.data.has_value
        assert diamagnetic_flux.data_error_upper.has_value
        assert diamagnetic_flux.data.coordinates[0].has_value

