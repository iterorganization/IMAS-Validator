@validator("equilibrium")  # noqa: F821
def validate_test_rule_fail(eq):
    assert eq.ids_properties.homogeneous_time > 2, "Oh noes it didn't work"
