import traceback
from pathlib import Path
from xml.dom import minidom

from ids_validator.report.validationResultGenerator import ValidationResultGenerator
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result import IDSValidationResult


def dummy_rule_function() -> None:
    pass


def test_error_result() -> None:
    # Create an error result, similar to ResultCollector.add_error_result()
    result = IDSValidationResult(
        False,
        "",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {},
        exc=RuntimeError("Dummy exception"),
        imas_uri="my_cool_uri",
    )
    result_generator = ValidationResultGenerator([result])

    tb = "\n".join(result.tb.format())
    node_text = minidom.Document().createTextNode(tb)
    str_to_compare = node_text.data.replace('"', "&quot;")
    str_to_compare = str_to_compare.replace(">", "&gt;")
    str_to_compare = str_to_compare.replace("<", "&lt;")
    assert result_generator._junit_xml == (
        f'<testsuites id="1" name="ids_validator" tests="1" failures="1">\n\t'
        f'<testsuite id="1.1" name="core_profiles-0" tests="1" failures="1">\n\t\t'
        f'<testcase id="1.1.1" name="to/rule.py/dummy_rule_function">\n\t\t\t'
        f'<failure message="" type="" nodes_dict="{{}}">{str(str_to_compare)}'
        f"</failure>\n\t\t"
        f"</testcase>\n\t"
        f"</testsuite>\n"
        f"</testsuites>\n"
    )

    last_tb = str(result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")
    assert result_generator._junit_txt == (
        f"Summary Report : \n"
        f"Number of tests carried out : 1\n"
        f"Number of successful tests : 0\n"
        f"Number of failed tests : 1\n\n"
        f"IDS core_profiles occurrence 0\n\n"
        f"Test with rule name : to/rule.py/dummy_rule_function, failed\n\t\t"
        f"Message : \n\t\t"
        f"Traceback : {str(last_tb)}\n\t\t"
        f"Nodes_Dict : {{}}\n"
    )


def test_successful_assert() -> None:
    # Create a successful assert result, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        True,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ["a", "b", "c"]},
        exc=None,
        imas_uri="my_cool_uri",
    )
    result_generator = ValidationResultGenerator([result])
    assert result_generator._junit_xml == (
        '<testsuites id="1" name="ids_validator" tests="1" failures="0">\n\t'
        '<testsuite id="1.1" name="core_profiles-0" tests="1" failures="0">\n\t\t'
        '<testcase id="1.1.1" name="to/rule.py/dummy_rule_function"/>\n\t'
        "</testsuite>\n"
        "</testsuites>\n"
    )

    assert result_generator._junit_txt == (
        "Summary Report : \n"
        "Number of tests carried out : 1\n"
        "Number of successful tests : 1\n"
        "Number of failed tests : 0\n\n"
        "IDS core_profiles occurrence 0\n\t"
        "Test with rule name : to/rule.py/dummy_rule_function, was successful\n"
    )


def test_failed_assert() -> None:
    # Create a failed assert esult, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        False,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ["a", "b", "c"]},
        exc=None,
        imas_uri="my_cool_uri",
    )
    result_generator = ValidationResultGenerator([result])

    tb = "\n".join(result.tb.format())
    node_text = minidom.Document().createTextNode(tb)
    str_to_compare = node_text.data.replace('"', "&quot;")
    str_to_compare = str_to_compare.replace(">", "&gt;")
    str_to_compare = str_to_compare.replace("<", "&lt;")
    assert result_generator._junit_xml == (
        f'<testsuites id="1" name="ids_validator" tests="1" failures="1">\n\t'
        f'<testsuite id="1.1" name="core_profiles-0" tests="1" failures="1">\n\t\t'
        f'<testcase id="1.1.1" name="to/rule.py/dummy_rule_function">\n\t\t\t'
        f'<failure message="Optional message" type="" '
        f"nodes_dict=\"{{('core_profiles', 0): ['a', 'b', 'c']}}\">"
        f"{str_to_compare}"
        f"</failure>\n\t\t"
        f"</testcase>\n\t"
        f"</testsuite>\n"
        f"</testsuites>\n"
    )

    last_tb = str(result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")
    assert result_generator._junit_txt == (
        f"Summary Report : \n"
        f"Number of tests carried out : 1\n"
        f"Number of successful tests : 0\n"
        f"Number of failed tests : 1\n\n"
        f"IDS core_profiles occurrence 0\n\n"
        f"Test with rule name : to/rule.py/dummy_rule_function, failed\n\t\t"
        f"Message : Optional message\n\t\t"
        f"Traceback : {str(last_tb)}\n\t\t"
        f"Nodes_Dict : {{('core_profiles', 0): ['a', 'b', 'c']}}\n"
    )
