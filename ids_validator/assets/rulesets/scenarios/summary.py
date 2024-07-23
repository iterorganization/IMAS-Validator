"""Validation rules of ITER scenario database for the ``summary`` IDS."""

@validator("summary")
def validate_mandatory_values(ids):
    """Validate that mandatory quantities are provided."""

    # time
    assert ids.time.has_value

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
    assert ids.local.separatrix.n_e.value.has_value
    assert ids.local.separatrix.n_i.has_value
    assert ids.local.separatrix.zeff.value.has_value
