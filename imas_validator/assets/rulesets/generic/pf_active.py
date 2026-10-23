"""Generic rules applying to the PF_ACTIVE IDS"""

@validator("pf_active", version="<4")
def validate_coil_name(ids):
    """Validate that pf_active/coil/name is filled in a unique way

    Only for DD < 4: from DD 4 on, uniqueness is checked by
    ``generic/generic.py:validate_unique_names``.
    """
    name_list = [str(coil.name) for coil in ids.coil]
    assert all(len(ele) > 0 for ele in name_list), "All coil/name nodes must be filled"
    assert len(name_list) == len(set(name_list)), "Each coil/name must be unique"
