# Generic rules applying to all IDSs


@validator("*")
def validate_homogeneous_time(ids):
    """Validation function for the time mode (ids_properties.homogeneous_time).

    Executed validations are:

    * homogeneous_time must be set to a valid value (0, 1 or 2)
    * "Static" IDSs must have homogeneous_time = 2
    * Root time must be non-empty when homogeneous_time = 1
    * All dynamic quantities must be empty when homogeneous_time = 2
    """
    assert 0 <= ids.ids_properties.homogeneous_time <= 2
    if not hasattr(ids, "time"):  # static IDSs don't have a root time attribute
        assert (
            ids.ids_properties.homogeneous_time == 2
        ), "Static IDS must have homogeneous_time == 2."

    if ids.ids_properties.homogeneous_time == 1:
        assert ids.time.has_value, "time must be non-empty when homogeneous_time == 1"

    if ids.ids_properties.homogeneous_time == 2:
        # Loop over all filled quantities and assert they are not dynamic
        for node in Select(ids, ".*", has_value=True):
            # Use IMASPy's metadata to check that this quantity is not dynamic
            # https://sharepoint.iter.org/departments/POP/CM/IMDesign/Code%20Documentation/IMASPy-doc/generated/imaspy.ids_metadata.IDSType.html#imaspy.ids_metadata.IDSType
            assert (
                not node.metadata.type.is_dynamic
            ), f"Dynamic quantity {node!r} may not be filled when homogeneous_time == 2"

