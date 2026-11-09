"""Generic rules applying to the equilibrium IDS

Sign conventions (COCOS) of the equilibrium IDS are verified in cocos.py.
"""

@validator("equilibrium")
def validate_pressure_non_negative(ids):
    """Validate that the pressure profile is non-negative in the EQUILIBRIUM IDS"""
    for time_slice in ids.time_slice:
        if time_slice.profiles_1d.pressure.has_value:
            assert (
                time_slice.profiles_1d.pressure >= 0
            ), "Pressure profile must be non-negative"
