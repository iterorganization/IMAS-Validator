# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("core_profiles")
def validate_values(ids):
    """Validate that -17 MA <= global_quantities.ip <= 0"""

    assert -17000000.0 <= ids.global_quantities.ip <= 0.0


@validator("core_profiles")
def validate_values(ids):
    """Validate that profiles_1d.q > 0"""

    for profiles_1d in ids.profiles_1d:
        assert 0. < profiles_1d.q
