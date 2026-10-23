"""Generic rules applying to all identifier structures.

Identifier structures (``name``, ``index``, ``description``) refer to an identifier
enumeration of the Data Dictionary, see
https://imas-data-dictionary.readthedocs.io/en/latest/reference_identifier.html
"""

from pathlib import Path

import imas
import numpy as np


def _metadata_identifier_enum(metadata):
    """Resolve an identifier enumeration. Some older DDs (3.22.0 to 4.0.0) refer to
    identifier files without their "_identifier" suffix; identifiers that still
    cannot be resolved are skipped."""
    try:
        return metadata.identifier_enum
    except KeyError:
        name = f"{Path(metadata.doc_identifier).stem}_identifier"
        if name in imas.identifiers.identifiers:
            return imas.identifiers[name]
        return None


def _identifier_enum(index):
    """Return the identifier enumeration of the structure containing ``index``, or
    None when that structure is not an identifier with an enumeration."""
    return _metadata_identifier_enum(Parent(index)._obj.metadata)


@validator("*")
def validate_identifier_index(ids):
    """Validate that identifier indices are defined in their identifier enumeration.

    Negative indices are not checked: the Data Dictionary specifies that "private
    identifier values must be indicated by a negative index".
    """
    for index in Select(ids, "(^|/)index$", has_value=True):
        identifier_enum = _identifier_enum(index)
        if identifier_enum is None or index < 0:
            continue
        assert np.isin(
            index, [member.index for member in identifier_enum]
        ), f"Identifier index is not defined in {identifier_enum.__name__}"


@validator("*")
def validate_identifier_name(ids):
    """Validate that identifier names match the name (or an alias) of the
    identifier enumeration value with the same index.

    Only checked when both ``name`` and ``index`` are filled and the index is
    defined in the identifier enumeration.
    """
    for index in Select(ids, "(^|/)index$", has_value=True):
        identifier_enum = _identifier_enum(index)
        if identifier_enum is None:
            continue
        name = Parent(index).name
        if not name.has_value:
            continue
        member = next((m for m in identifier_enum if index == m.index), None)
        if member is None:  # Reported by validate_identifier_index
            continue
        assert np.logical_and(
            index == member.index, np.isin(name, [member.name, *member.aliases])
        ), (
            f"Identifier name does not match '{member.name}' (index {member.index})"
            f" of {identifier_enum.__name__}"
        )


def _plural_identifier_enum(indices):
    """Resolve plural identifiers, including the enclosing GGD declaration."""
    metadata = Parent(indices)._obj.metadata
    if not getattr(metadata, "structure_reference", "").startswith("identifier_"):
        return None
    identifier_enum = _metadata_identifier_enum(metadata)
    if identifier_enum is None:
        parent = Parent(indices, 2)._obj.metadata
        if getattr(parent, "structure_reference", "") == "generic_grid_identifier":
            identifier_enum = _metadata_identifier_enum(parent)
    return identifier_enum


@validator("*")
def validate_identifier_indices(ids):
    """Check plural identifier indices against their DD enumeration.

    Negative (private) values and structures without an enumeration are skipped.
    """
    for indices in Select(ids, "(^|/)indices$", has_value=True):
        identifier_enum = _plural_identifier_enum(indices)
        if identifier_enum is None:
            continue
        allowed = [member.index for member in identifier_enum]
        for position, index in enumerate(indices):
            if index < 0:
                continue
            assert np.isin(index, allowed), (
                f"Identifier index at position {position} is not defined in "
                f"{identifier_enum.__name__}"
            )


@validator("*")
def validate_identifier_names(ids):
    """Check plural names against the canonical names or aliases of their indices.

    A single name or index applies to every element of the subset. Otherwise,
    filled arrays must have equal lengths. Empty names and private or unknown
    indices are skipped; unknown indices are checked by validate_identifier_indices.
    """
    for indices in Select(ids, "(^|/)indices$", has_value=True):
        identifier_enum = _plural_identifier_enum(indices)
        if identifier_enum is None:
            continue
        names = Parent(indices).names
        if not names.has_value:
            continue
        if len(indices) != len(names) and len(indices) != 1 and len(names) != 1:
            assert np.size(indices) == np.size(names), (
                "Identifier indices and names must have equal lengths "
                "unless one array has length 1"
            )
            continue
        for position in range(max(len(indices), len(names))):
            index = indices[0 if len(indices) == 1 else position]
            name = names[0 if len(names) == 1 else position]
            if index < 0 or not name:
                continue
            member = next((m for m in identifier_enum if index == m.index), None)
            if member is None:
                continue
            assert np.logical_and(
                index == member.index, np.isin(name, [member.name, *member.aliases])
            ), (
                f"Identifier name at position {position} does not match "
                f"'{member.name}' (index {member.index}) of {identifier_enum.__name__}"
            )
