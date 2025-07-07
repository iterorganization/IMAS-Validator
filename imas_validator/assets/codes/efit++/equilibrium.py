"""Required fields of EFIT++ in the equilibrium IDS"""

@validator("equilibrium")
def validate_required_fields(ids):
    """
    Validate that the equilibrium IDS has required fields.
    """

    # Equilibrium constraints
    for time_slice in ids.time_slice:
        assert time_slice.constraints.ip.weight.has_value
        assert time_slice.constraints.diamagnetic_flux.weight.has_value

        for pf_current in time_slice.constraints.pf_current:
            assert pf_current.source.has_value
            assert pf_current.weight.has_value

        for pf_passive_current in time_slice.constraints.pf_passive_current:
            assert pf_passive_current.source.has_value

        for bpol_probe in time_slice.constraints.bpol_probe:
            assert bpol_probe.weight.has_value

        for flux_loop in time_slice.constraints.flux_loop:
            assert flux_loop.weight.has_value
