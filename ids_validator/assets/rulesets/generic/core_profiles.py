"""Generic rules applying to the core_profiles IDS"""

@validator("core_profiles")
def validate_electroneutrality_core_profiles(ids):
    """Validate that electroneutrality is verified in the CORE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].density.has_value:
            continue
        ni_zi = sum(ion.density * ion.z_ion for ion in profiles_1d.ion)
        assert Approx(
            profiles_1d.electrons.density,
            ni_zi,
        ), "Electroneutrality is not verified"


@validator("core_profiles")
def validate_z_ion_core_profiles(ids):
    """Validate that the ion average charge z_ion is consistent
    with ion elements in the CORE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].z_ion.has_value:
            continue
        for ion in profiles_1d.ion:
            if len(ion.element) == 0:
                assert len(ion.element) > 0, "ion/element structure must be allocated"
            else:
                zi = sum(abs(element.z_n) * element.atoms_n for element in ion.element)
                assert (
                    0 < abs(ion.z_ion) <= zi
                ), "Average ion charge above the summed nuclear charge of ion elements"


@validator("core_profiles")
def validate_pressure_thermal_electron_core_profiles(ids):
    """Validate that the electron thermal pressure is consistent
    with density_thermal and temperature in the CORE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if not (
            profiles_1d.electrons.temperature.has_value
            and profiles_1d.electrons.density_thermal.has_value
            and profiles_1d.electrons.pressure_thermal.has_value
        ):
            continue
        assert Approx(
            profiles_1d.electrons.pressure_thermal,
            profiles_1d.electrons.density_thermal
            * profiles_1d.electrons.temperature
            * 1.6022e-19,
        ), "Electron thermal pressure not consistent with density_thermal * temperature"
