try:
    import imaspy as imas  # type: ignore
    from imaspy.test.test_helpers import fill_consistent # type: ignore
except ImportError:
    import imas  # type: ignore
    from imas.test.test_helpers import fill_consistent # type: ignore
import pytest
from packaging.version import Version

from imas_validator.validate.validate import validate


@pytest.mark.skipif(
    Version(imas.__version__) < Version("1.1"),
    reason="fill_consistent needs arg leave_empty",
)
@pytest.mark.parametrize("ids_name", imas.IDSFactory().ids_names())
def test_generic_tests_with_randomly_generated_ids(ids_name, tmp_path):
    if ids_name == "amns_data":
        pytest.skip("amns_data IDS is not supported by IMAS-Python's fill_consistent")

    ids = imas.IDSFactory().new(ids_name)
    fill_consistent(ids, leave_empty=0)

    uri = f"{tmp_path}/pulse.nc"
    dbentry = imas.DBEntry(uri, "w")
    dbentry.put(ids)
    dbentry.close()

    results_collection = validate(uri)
    assert len(results_collection.results) > 0
    for result in results_collection.results:
        # Generic tests should generally not lead to an Exception
        # fill_consistent might create incompatible ggd ion and density data
        assert result.exc is None or (
            "operands could not be broadcast together" in str(result.exc)
        )
