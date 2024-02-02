@ids_validator("core_profiles")  # noqa: F821
def validate_test_rule_success(cp):
    assert cp.ids_properties.homogeneous_time == 1
