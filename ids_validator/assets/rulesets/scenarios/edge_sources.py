"""Validation rules of ITER scenario database for the ``edge_sources`` IDS."""


@validator("edge_sources")
def validate_mandatory_values(ids):
    """Validate that mandatory quantities are provided."""

    # time
    assert ids.time.has_value

    # output_flag
    # assert ids.output_flag.has_value

    # source
    assert ids.source.has_value
    for source in ids.source:

        # source[:].ggd
        assert source.ggd
        for ggd in source.ggd:

            assert ggd.time.has_value

            # source[:].ggd[:].ion
            assert ggd.ion.has_value
            for ion in ggd.ion:

                # source[:].ggd[:].ion[:].element
                assert ion.element.has_value
                for element in ion.element:

                    assert element.a.has_value
                    assert element.z_n.has_value
                    assert element.atoms_n.has_value

                assert ion.multiple_states_flag.has_value

                # source[:].ggd[:].ion[:].state
                assert ion.state.has_value
                for state in ion.state:

                    assert state.z_min.has_value
                    assert state.z_max.has_value

            # source[:].ggd[:].neutral
            assert ggd.neutral.has_value
            for neutral in ggd.neutral:

                # source[:].ggd[:].neutral[:].state
                assert neutral.state.has_value
                for state in neutral.state:

                    assert state.neutral_type.name.has_value
