import imaspy
import pytest
from imaspy.test.test_helpers import fill_consistent

from ids_validator.validate.validate import validate


@pytest.mark.parametrize("ids_name", imaspy.IDSFactory().ids_names())
def test_generic_tests_with_randomly_generated_ids(ids_name, tmp_path):
    if ids_name == "amns_data":
        pytest.skip("amns_data IDS is not supported by IMASPy's fill_consistent")

    ids = imaspy.IDSFactory().new(ids_name)
    fill_consistent(ids)

    uri = f"imas:ascii?path={tmp_path}"
    dbentry = imaspy.DBEntry(uri, "w")
    dbentry.put(ids)
    dbentry.close()

    results_collection = validate(uri)
    assert len(results_collection.results) > 0
    for result in results_collection.results:
        assert result.exc is None  # Generic tests should not lead to an Exception
