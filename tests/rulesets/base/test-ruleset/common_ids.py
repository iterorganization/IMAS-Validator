@validator("*")  # noqa: F821
def common_ids_rule(ids):
    ids is not None
