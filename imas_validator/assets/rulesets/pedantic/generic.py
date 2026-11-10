"""Pedantic rules applying to all IDSs"""

from imas.ids_data_type import IDSDataType


@validator("*")
def validate_aos_name_not_empty(ids):
    """Validate that every ``name`` field located directly under an Array of
    Structures is filled with a non-empty (non-whitespace) string, for each
    allocated element of the Array of Structures.
    """
    for name in Select(ids, "(^|/)name$", has_value=False):
        # Skip names of the IDS toplevel or of plain structures (e.g. code/name)
        if Parent(name).metadata.data_type != IDSDataType.STRUCT_ARRAY:
            continue
        assert name.strip() != "", "Empty name for an element of an Array of Structures"
