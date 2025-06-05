"""Validation rules of ITER scenario database for the ``edge_profiles`` IDS."""

@validator("edge_profiles")
def validate_mandatory_values(ids):
    """Validate that mandatory quantities are provided."""

    # time
    assert ids.time.has_value

    # vacuum_toroidal_field
    assert ids.vacuum_toroidal_field.r0.has_value
    assert ids.vacuum_toroidal_field.b0.has_value

    # ggd
    assert ids.ggd.has_value
    for ggd in ids.ggd:

        assert ggd.time.has_value

        # ggd[:].electrons.temperature
        assert ggd.electrons.temperature.has_value
        for temperature in ggd.electrons.temperature:

            assert temperature.values.has_value

        assert ggd.electrons.velocity.has_value

        # ggd[:].electrons.phi_potential
        assert ggd.phi_potential.has_value
        for phi_potential in ggd.phi_potential:
            assert phi_potential.values.has_value

        # ggd[:].ion
        assert ggd.ion.has_value
        for ion in ggd.ion:

            # ggd[:].ion[:].element
            assert ion.element.has_value
            for element in ion.element:

                assert element.a.has_value
                assert element.z_n.has_value
                assert element.atoms_n.has_value

            assert ion.multiple_states_flag.has_value

            # ggd[:].ion[:].state
            assert ion.state.has_value
            for state in ion.state:

                assert state.z_min.has_value

                assert state.z_max.has_value
                for density in state.density:

                    assert density.values.has_value

                assert state.velocity.has_value

        # ggd[:].neutral
        assert ggd.neutral.has_value
        for neutral in ggd.neutral:

            assert neutral.ion_index.has_value

            # ggd[:].neutral[:].element
            assert neutral.element.has_value
            for element in neutral.element:

                assert element.a.has_value
                assert element.z_n.has_value
                assert element.atoms_n.has_value

            assert neutral.multiple_states_flag.has_value

            # ggd[:].neutral[:].density
            assert neutral.density.has_value
            for density in neutral.density:

                assert density.values.has_value

            # ggd[:].neutral[:].state
            assert neutral.state.has_value
            for state in neutral.state:

                assert state.neutral_type.name.has_value

                assert state.density.has_value
                for density in state.density:

                    assert density.values.has_value

                # path of neutral velocity is ambiguous in the ref
                assert state.velocity.has_value
