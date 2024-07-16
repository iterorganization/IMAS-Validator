# https://confluence.iter.org/display/IMP/Required+fields+in+a+dataset+to+be+imported+in+a+scenario+database


@validator("edge_transport")
def validate_mandatory_values(ids):
    """Validate if the property exists by using has_value method in IMASPy."""

    # time
    assert ids.time.has_value

    # output_flag
    # assert ids.output_flag.has_value

    # model
    assert ids.model.has_value
    for model in ids.model:

        assert model.flux_multiplier.has_value

        # model[:].ggd
        assert model.ggd.has_value
        for ggd in model.ggd:

            assert ggd.time.has_value

            # model[:].ggd[:].electrons.flux
            assert ggd.electrons.energy.flux.has_value
            for flux in ggd.electrons.energy.flux:

                assert flux.values.has_value

            # model[:].ggd[:].particles.flux
            assert ggd.electrons.particles.flux.has_value
            for flux in ggd.electrons.particles.flux:

                assert flux.values.has_value

            # model[:].ggd[:].ion
            assert ggd.ion.has_value
            for ion in ggd.ion:

                # model[:].ggd[:].ion[:].element
                assert ion.element.has_value
                for element in ion.element:

                    assert element.a.has_value
                    assert element.z_n.has_value
                    assert element.atoms_n.has_value

                # model[:].ggd[:].ion[:].multiple_states
                assert ion.multiple_states_flag.has_value

                # model[:].ggd[:].ion[:].state
                assert ion.state.has_value
                for state in ion.state:

                    assert state.z_min.has_value
                    assert state.z_max.has_value

                    # model[:].ggd[:].ion[:].state.particles.flux
                    assert state.particles.flux.has_value
                    for flux in state.particles.flux:

                        assert flux.values.has_value

                    # model[:].ggd[:].ion[:].state.energy.flux
                    assert state.energy.flux.has_value
                    for flux in state.energy.flux:

                        assert flux.values.has_value

            # model[:].ggd[:].neutral
            assert ggd.neutral.has_value
            for neutral in ggd.neutral:

                # model[:].ggd[:].neutral[:].state
                assert neutral.state.has_value
                for state in neutral.state:

                    assert state.neutral_type.name.has_value

                    # model[:].ggd[:].neutral[:].state.energy.flux
                    assert state.energy.flux.has_value
                    for flux in state.energy.flux:

                        assert flux.values.has_value

                    # model[:].ggd[:].neutral[:].state.particles.flux
                    assert state.particles.flux.has_value
                    for flux in state.particles.flux:

                        assert flux.values.has_value
