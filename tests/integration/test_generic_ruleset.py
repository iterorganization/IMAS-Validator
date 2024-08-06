import imaspy
import pytest
from imaspy.test.test_helpers import fill_consistent
from packaging.version import Version

from ids_validator.validate.validate import validate


@pytest.mark.skipif(
    Version(imaspy.__version__) < Version("1.1"),
    reason="fill_consistent needs arg leave_empty",
)
@pytest.mark.parametrize("ids_name", imaspy.IDSFactory().ids_names())
def test_generic_tests_with_randomly_generated_ids(ids_name, tmp_path):
    if ids_name == "amns_data":
        pytest.skip("amns_data IDS is not supported by IMASPy's fill_consistent")

    ids = imaspy.IDSFactory().new(ids_name)
    fill_consistent(ids, leave_empty=0)

    uri = f"imas:ascii?path={tmp_path}"
    dbentry = imaspy.DBEntry(uri, "w")
    dbentry.put(ids)
    dbentry.close()

    results = validate(uri)
    assert len(results) > 0
    for result in results:
        assert result.exc is None  # Generic tests should not lead to an Exception
