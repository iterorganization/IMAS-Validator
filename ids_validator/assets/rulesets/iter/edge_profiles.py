# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("edge_profiles")
def validate_vacuum_toroidal_field_b0(ids):
    """Validate that vacuum_toroidal_field/b0(:) is -8 T < b0 < 0 T"""

    assert -8.0 <= ids.vacuum_toroidal_field.b0 <= 0.0
