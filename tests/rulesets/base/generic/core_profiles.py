# Do not add additional validation tests as this file is used by tests/test_loading.py


@validator("core_profiles")  # noqa: F821
def core_profiles_rule(cp):
    assert cp is not None


# Ensure helpers are available
Select  # noqa: F821
Increasing  # noqa: F821
Decreasing  # noqa: F821
Approx  # noqa: F821
