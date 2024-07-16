# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("summary")
def validate_mandatory_values(ids):
    """Validate if the property exists by using has_value method in IMASPy."""

    # global_quantities
    assert -8.0 <= ids.global_quantities.b0.value <= 0.0
    assert  4.1 <= ids.global_quantities.r0.value <= 8.5
    assert -17000000.0 <= ids.global_quantities.ip.value <= 0.0
    assert 0 <= ids.global_quantities.q_95.value
