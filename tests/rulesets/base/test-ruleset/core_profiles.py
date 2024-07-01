"""Module level docstring for validation tests"""

@validator("core_profiles")  # noqa: F821
def core_profiles_rule(cp):
    """Function level docstring for validation tests"""
    cp is not None
