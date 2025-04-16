"""Generic rules applying to the PF_ACTIVE IDS"""

@validator("pf_active")
def validate_coil_name(ids):
    """Validate that pf_active/coil/name is filled in a unique way"""
    name_list = [str(coil.name) for coil in ids.coil]
    assert all(len(ele) > 0 for ele in name_list), "All coil/name nodes must be filled"
    assert len(name_list) == len(set(name_list)), "Each coil/name must be unique"
