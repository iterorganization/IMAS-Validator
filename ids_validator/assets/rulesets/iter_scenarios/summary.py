# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("summary")
def validate_mandatory_values(ids):
    """Validate if the property exists by using has_value method in IMASPy."""

    # time
    assert ids.time.has_value

    # output_flag
    # assert ids.output_flag.has_value

    # global_quantities
    assert ids.global_quantities.b0.value.has_value
    assert ids.global_quantities.r0.value.has_value
    assert ids.global_quantities.beta_pol.value.has_value
    assert ids.global_quantities.beta_tor_norm.value.has_value
    assert ids.global_quantities.current_bootstrap.value.has_value
    assert ids.global_quantities.current_non_inductive.value.has_value
    assert ids.global_quantities.current_ohm.value.has_value
    assert ids.global_quantities.energy_diamagnetic.value.has_value
    assert ids.global_quantities.energy_thermal.value.has_value
    assert ids.global_quantities.energy_total.value.has_value
    assert ids.global_quantities.h_98.value.has_value
    assert ids.global_quantities.h_mode.value.has_value
    assert ids.global_quantities.ip.value.has_value
    assert ids.global_quantities.tau_energy.value.has_value
    assert ids.global_quantities.v_loop.value.has_value
    assert ids.global_quantities.q_95.value.has_value

    # local
    assert ids.local.separatrix.n_e.value.has_value
    # local.separatrix.n_i.*.value
    assert ids.local.separatrix.n_i.has_value
    assert ids.local.separatrix.zeff.value.has_value


@validator("summary")
def validate_global_quantities_b0(ids):
    """Validate that global_quantities/b0/value(:) is b0 < 0."""

    assert ids.global_quantities.b0.value < 0.0


@validator("summary")
def validate_global_quantities_ip(ids):
    """Validate that global_quantities/ip/value(:) is -17000000 < ip <= 0."""

    assert -17000000 < ids.global_quantities.ip.value <= 0.0
