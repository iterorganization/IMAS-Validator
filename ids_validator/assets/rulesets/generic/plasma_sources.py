"""Generic rules applying to the plasma_sources IDS"""

@validator("plasma_sources")
def validate_z_ion(ids):
    """Validate that the ion average charge z_ion is consistent
    with ion elements in the PLASMA_SOURCES IDS"""
    for source in ids.source:
       for profiles_1d in source.profiles_1d:
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
       for ggd in source.ggd:
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
