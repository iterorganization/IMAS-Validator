@ids_validator("core_profiles")  # noqa: F821
def validate_test_rule_success(cp):
    assert cp.ids_properties.homogeneous_time == 1


@ids_validator("core_profiles")  # noqa: F821
def validate_test_rule_error(cp):
    1 / 0
    assert cp.ids_properties.homogeneous_time == 1
