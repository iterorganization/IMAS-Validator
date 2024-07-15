"""Module level docstring for validation tests"""

@validator("*")  # noqa: F821
def common_ids_rule(ids):
    """Function level docstring for validation tests"""
    ids is not None
