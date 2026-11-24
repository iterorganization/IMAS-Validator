"""Identifier index/name checks against imas-python's bundled DD enumerations.
Negative (private) indices and names unknown to the bundled enumeration are skipped."""

from pathlib import Path

import imas
import numpy as np


def _metadata_identifier_enum(metadata):
    """Resolve the identifier enumeration, also for older DDs whose reference lacks
    the "_identifier" suffix; None if it cannot be resolved."""
    try:
        return metadata.identifier_enum
    except KeyError:
        name = f"{Path(metadata.doc_identifier).stem}_identifier"
        if name in imas.identifiers.identifiers:
            return imas.identifiers[name]
        return None


def _unknown_name(identifier_enum, name):
    """Whether ``name`` is no name or alias of the enumeration, ignoring case
    (it may be valid in the data's own DD version)."""
    value = str(getattr(name, "value", name)).casefold()
    return all(
        value not in (n.casefold() for n in (m.name, *m.aliases))
        for m in identifier_enum
    )


def _identifier_enum(index):
    """Identifier enumeration of the structure containing ``index``, or None."""
    return _metadata_identifier_enum(Parent(index)._obj.metadata)


@validator("*")
def validate_identifier_index(ids):
    """Validate that identifier indices are defined in their enumeration.
    Negative (private) indices are skipped."""
    for index in Select(ids, "(^|/)index$", has_value=True):
        identifier_enum = _identifier_enum(index)
        if identifier_enum is None or index < 0:
            continue
        assert np.isin(
            index, [member.index for member in identifier_enum]
        ), f"Identifier index is not defined in {identifier_enum.__name__}"


@validator("*")
def validate_identifier_name(ids):
    """Validate that identifier names match the name or an alias of their index.
    Names unknown to the bundled enumeration are skipped."""
    for index in Select(ids, "(^|/)index$", has_value=True):
        identifier_enum = _identifier_enum(index)
        if identifier_enum is None:
            continue
        name = Parent(index).name
        if not name.has_value or index < 0:
            continue
        member = next((m for m in identifier_enum if index == m.index), None)
        if member is None:  # Reported by validate_identifier_index
            continue
        if _unknown_name(identifier_enum, name._obj):
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
    """Validate that plural identifier indices are defined in their enumeration.
    Negative (private) indices are skipped."""
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
    """Validate that plural names match the name or an alias of their indices.
    A length-1 array applies to all elements; unknown names are skipped."""
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
            if _unknown_name(identifier_enum, getattr(name, "_obj", name)):
                continue
            assert np.logical_and(
                index == member.index, np.isin(name, [member.name, *member.aliases])
            ), (
                f"Identifier name at position {position} does not match "
                f"'{member.name}' (index {member.index}) of {identifier_enum.__name__}"
            )
