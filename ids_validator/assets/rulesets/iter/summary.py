"""ITER-specific validation rules for the ``summary`` IDS."""


@validator("summary")
def validate_mandatory_values(ids):
    """Validate data in IDS/summary against rulesets for ITER scenario."""

    # global_quantities
    assert -8.0 <= ids.global_quantities.b0.value <= 0.0
    assert 4.1 <= ids.global_quantities.r0.value <= 8.5
    assert -17000000.0 <= ids.global_quantities.ip.value <= 0.0
    assert 0 <= ids.global_quantities.q_95.value
