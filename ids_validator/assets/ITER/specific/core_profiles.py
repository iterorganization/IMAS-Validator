# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("core_profiles")
def validate_mandatory_values(ids):
    """Validate if the property exists by using has_value method in IMASPy."""

    # global_quantities
    assert ids.global_quantities.beta_pol.has_value
    assert ids.global_quantities.beta_tor_norm.has_value
    assert ids.global_quantities.current_bootstrap.has_value
    assert ids.global_quantities.current_non_inductive.has_value
    assert ids.global_quantities.energy_diamagnetic.has_value
    assert ids.global_quantities.ip.has_value
    assert ids.global_quantities.v_loop.has_value

    # profiles_1d
    assert ids.profiles_1d.has_value
    for profiles_1d in ids.profiles_1d:
        assert profiles_1d.e_field.radial.has_value
        assert profiles_1d.electrons.density.has_value
        assert profiles_1d.electrons.pressure.has_value
        assert profiles_1d.electrons.pressure_fast_parallel.has_value
        assert profiles_1d.electrons.pressure_fast_perpendicular.has_value
        assert profiles_1d.electrons.pressure_thermal.has_value
        assert profiles_1d.electrons.temperature.has_value
        assert profiles_1d.grid.rho_tor.has_value
        assert profiles_1d.grid.rho_tor_norm.has_value
        assert profiles_1d.grid.psi.has_value
        assert profiles_1d.grid.volume.has_value

        # profiles_1d[:].ion
        assert profiles_1d.ion.has_value
        for ion in profiles_1d.ion:

            assert ion.density.has_value

            # profiles_1d[:].ion[:].element
            assert ion.element.has_value
            for element in ion.element:

                assert element.a.has_value
                assert element.z_n.has_value

            assert ion.pressure.has_value
            assert ion.pressure_fast_parallel.has_value
            assert ion.pressure_fast_perpendicular.has_value
            assert ion.pressure_thermal.has_value
            assert ion.temperature.has_value
            assert ion.velocity.diamagnetic.has_value
            assert ion.velocity.poloidal.has_value
            assert ion.velocity.toroidal.has_value

        assert profiles_1d.j_bootstrap.has_value
        assert profiles_1d.j_non_inductive.has_value
        assert profiles_1d.j_ohmic.has_value
        assert profiles_1d.j_total.has_value
        assert profiles_1d.magnetic_shear.has_value
        assert profiles_1d.pressure_ion_total.has_value
        assert profiles_1d.pressure_parallel.has_value
        assert profiles_1d.pressure_perpendicular.has_value
        assert profiles_1d.pressure_thermal.has_value
        assert profiles_1d.q.has_value
        assert profiles_1d.t_i_average.has_value
        assert profiles_1d.zeff.has_value


@validator("core_profiles")
def validate_global_quantities_ip(ids):
    """Validate that global_quantities/ip(:) is in range of -17MA < ip <= 0."""

    assert -17000000.0 < ids.global_quantities.ip <= 0.0
