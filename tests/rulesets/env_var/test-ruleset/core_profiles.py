@validator("core_profiles")  # noqa: F821
def core_profiles_rule(cp):
    cp is not None
