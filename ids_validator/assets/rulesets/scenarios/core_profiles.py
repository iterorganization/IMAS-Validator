# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("core_profiles")
def validate_mandatory_values(ids):
    """Validate that mandatory quantities are provided."""

    # profiles_1d
    assert ids.profiles_1d.has_value
    for profiles_1d in ids.profiles_1d:
        assert profiles_1d.electrons.density.has_value
        assert profiles_1d.electrons.pressure_thermal.has_value
        assert profiles_1d.electrons.temperature.has_value
        assert profiles_1d.grid.psi.has_value

        # profiles_1d[:].ion
        assert profiles_1d.ion.has_value
        for ion in profiles_1d.ion:

            assert ion.density.has_value

            # profiles_1d[:].ion[:].element
            assert ion.element.has_value
            for element in ion.element:

                assert element.a.has_value
                assert element.z_n.has_value

            assert ion.pressure_thermal.has_value
            assert ion.temperature.has_value

        assert profiles_1d.pressure_thermal.has_value
        assert profiles_1d.q.has_value
        assert profiles_1d.zeff.has_value
 
