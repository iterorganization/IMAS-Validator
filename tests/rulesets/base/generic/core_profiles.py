# Do not add additional validation tests as this file is used by tests/test_loading.py


@validator("core_profiles")  # noqa: F821
def core_profiles_rule(cp):
    assert cp is not None
