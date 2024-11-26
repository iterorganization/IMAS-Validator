"""Generic rules applying to the edge_profiles IDS"""

@validator("edge_profiles")
def validate_electroneutrality_1d(ids):
    """Validate that electroneutrality is verified in the EDGE_PROFILES IDS (profiles_1d)"""
    for profiles_1d in ids.profiles_1d:
        if len(profiles_1d.ion) == 0 or not profiles_1d.ion[0].density.has_value:
            continue
        ni_zi = sum(ion.density * ion.z_ion for ion in profiles_1d.ion)
        assert Approx(
            profiles_1d.electrons.density,
            ni_zi,
        ), "Electroneutrality is not verified"


@validator("edge_profiles")
def validate_electroneutrality_ggd(ids):
    """Validate that electroneutrality is verified in the EDGE_PROFILES IDS (ggd)"""
    for ggd in ids.ggd:
        if (
            len(ggd.ion) == 0
            or len(ggd.ion[0].density) == 0
            or len(ggd.electrons.density) == 0
            or not len(ggd.ion[0].density) == len(ggd.electrons.density)
        ):
            continue
        for subset in range(len(ggd.electrons.density)):
            ni_zi = sum(ion.density[subset].values * ion.z_ion for ion in ggd.ion)
            assert Approx(
                ggd.electrons.density[subset].values,
                ni_zi,
            ), "Electroneutrality is not verified"


@validator("edge_profiles")
def validate_z_ion(ids):
    """Validate that the ion average charge z_ion is consistent
    with ion elements in the EDGE_PROFILES IDS"""
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
    for ggd in ids.ggd:
        if len(ggd.ion) == 0 or not ggd.ion[0].z_ion.has_value:
            continue
        for ion in ggd.ion:
            if len(ion.element) == 0:
                assert len(ion.element) > 0, "ion/element structure must be allocated"
            else:
                zi = sum(abs(element.z_n) * element.atoms_n for element in ion.element)
                assert (
                    0 < abs(ion.z_ion) <= zi
                ), "Average ion charge above the summed nuclear charge of ion elements"


@validator("edge_profiles")
def validate_pressure_thermal_electron_edge_profiles(ids):
    """Validate that the electron thermal pressure is consistent
    with density_thermal and temperature in the EDGE_PROFILES IDS"""
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
            * 1.602176634e-19,
        ), "Electron thermal pressure not consistent with density_thermal * temperature"


@validator("edge_profiles")
def validate_zeff(ids):
    """Validate that the effective charge zeff is consistent
    with ion densities in the EDGE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if (
            len(profiles_1d.ion) == 0
            or not profiles_1d.zeff.has_value
            or not profiles_1d.electrons.density.has_value
            or not profiles_1d.ion[0].z_ion_square_1d.has_value
            or not profiles_1d.ion[0].density.has_value
        ):
            continue
        zeff = sum(ion.density * ion.z_ion_square_1d for ion in profiles_1d.ion) / (
            profiles_1d.electrons.density
        )
        assert Approx(
            profiles_1d.zeff, zeff
        ), "Effective charge zeff not consistent with ion square charge and density"


@validator("edge_profiles")
def validate_n_i_total_over_n_e(ids):
    """Validate that the total density ratio is consistent
    with ion and electron densities in the EDGE_PROFILES IDS"""
    for profiles_1d in ids.profiles_1d:
        if (
            len(profiles_1d.ion) == 0
            or not profiles_1d.n_i_total_over_n_e.has_value
            or not profiles_1d.electrons.density.has_value
            or not profiles_1d.ion[0].density.has_value
        ):
            continue
        n_i_total_over_n_e = sum(ion.density for ion in profiles_1d.ion) / (
            profiles_1d.electrons.density
        )
        assert Approx(
            profiles_1d.n_i_total_over_n_e, n_i_total_over_n_e
        ), "n_i_total_over_n_e not consistent with ion and electron densities"
