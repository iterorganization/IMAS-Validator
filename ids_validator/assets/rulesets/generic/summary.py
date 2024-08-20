"""Generic rules applying to the summary IDS"""

@validator("summary")
def validate_source_summary(ids):
    """Validate that whenever a value node is filled, the related source node is filled in the SUMMARY IDS"""
    for value in Select(ids, "value", has_value=True):
        source = getattr(Parent(value), "source", None)
        assert (
            source.has_value
        ), "Source node must be filled for any non-empty value node in the SUMMARY IDS"
