"""Required fields of EFIT++ in the wall IDS"""

@validator("wall")
def validate_required_fields(ids):
    """Validate that the wall IDS has required fields."""

    # Wall limiter 2d
    for description_2d in ids.description_2d:
        # machine description
        for unit in description_2d.limiter.unit:
            assert unit.outline.r.has_value
            assert unit.outline.z.has_value
