@validator("*")
def test_custom(ids):
    assert ids is not None
