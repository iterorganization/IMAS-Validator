import traceback
from datetime import datetime
from pathlib import Path
from xml.dom import minidom

import pytest

from ids_validator.report.validationResultGenerator import (
    SummaryReportGenerator,
    ValidationResultGenerator,
)
from ids_validator.rules.data import IDSValidationRule
from ids_validator.validate.result import (
    CoverageMap,
    IDSValidationResult,
    IDSValidationResultCollection,
)
from ids_validator.validate_options import ValidateOptions


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
    )

    uri = "imas:mdsplus?test_validationResultGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationResultGenerator(result_collection)

    tb = "\n".join(result.tb.format())
    node_text = minidom.Document().createTextNode(tb)
    str_to_compare = node_text.data.replace('"', "&quot;")
    str_to_compare = str_to_compare.replace(">", "&gt;")
    str_to_compare = str_to_compare.replace("<", "&lt;")
    assert result_generator.xml == (
        f'<testsuites id="1" name="ids_validator" tests="1" failures="1">\n\t'
        f'<testsuite id="1.1" name="core_profiles-0" tests="1" failures="1">\n\t\t'
        f'<testcase id="1.1.1" name="to/rule.py:dummy_rule_function">\n\t\t\t'
        f'<failure message="" type="" nodes_dict="{{}}">{str(str_to_compare)}'
        f"</failure>\n\t\t"
        f"</testcase>\n\t"
        f"</testsuite>\n"
        f"</testsuites>\n"
    )

    last_tb = str(result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")

    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        f"Summary Report : \n"
        f"Tested URI : imas:mdsplus?test_validationResultGeneratorUri\n"
        f"Number of tests carried out : 1\n"
        f"Number of successful tests : 0\n"
        f"Number of failed tests : 1\n\n"
        f"PASSED IDSs:"
        f"FAILED IDSs:"
        f"- IDS core_profiles occurrence 0"
        f"RULE: to/rule.py:dummy_rule_function"
        f"MESSAGE:"
        f"TRACEBACK: {last_tb}"
        f"NODES COUNT: 0"
        f"NODES: []"
        # f"Coverage map:"
    ).replace(
        "\t", ""
    ).replace(
        "\n", ""
    ).replace(
        " ", ""
    )


def test_successful_assert() -> None:
    # Create a successful assert result, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        True,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ("a", "b", "c")},
        exc=None,
    )
    uri = "imas:mdsplus?test_validationResultGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationResultGenerator(result_collection)
    assert result_generator.xml == (
        '<testsuites id="1" name="ids_validator" tests="1" failures="0">\n\t'
        '<testsuite id="1.1" name="core_profiles-0" tests="1" failures="0">\n\t\t'
        '<testcase id="1.1.1" name="to/rule.py:dummy_rule_function"/>\n\t'
        "</testsuite>\n"
        "</testsuites>\n"
    )

    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        "Summary Report : "
        "Tested URI : imas:mdsplus?test_validationResultGeneratorUri\n"
        "Number of tests carried out : 1"
        "Number of successful tests : 1"
        "Number of failed tests : 0"
        "PASSED IDSs:"
        "+ IDS core_profiles occurrence 0"
        "FAILED IDSs:"
        # "Coverage map:"
    ).replace(
        "\t", ""
    ).replace(
        "\n", ""
    ).replace(
        " ", ""
    )


def test_failed_assert() -> None:
    # Create a failed assert result, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        False,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ("a", "b", "c")},
        exc=None,
    )
    uri = "imas:mdsplus?test_validationResultGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationResultGenerator(result_collection)

    tb = "\n".join(result.tb.format())
    node_text = minidom.Document().createTextNode(tb)
    str_to_compare = node_text.data.replace('"', "&quot;")
    str_to_compare = str_to_compare.replace(">", "&gt;")
    str_to_compare = str_to_compare.replace("<", "&lt;")
    assert result_generator.xml == (
        f'<testsuites id="1" name="ids_validator" tests="1" failures="1">\n\t'
        f'<testsuite id="1.1" name="core_profiles-0" tests="1" failures="1">\n\t\t'
        f'<testcase id="1.1.1" name="to/rule.py:dummy_rule_function">\n\t\t\t'
        f'<failure message="Optional message" type="" '
        f"nodes_dict=\"{{('core_profiles', 0): {'a', 'b', 'c'}}}\">"
        f"{str_to_compare}"
        f"</failure>\n\t\t"
        f"</testcase>\n\t"
        f"</testsuite>\n"
        f"</testsuites>\n"
    )

    last_tb = str(result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")

    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        f"Summary Report : "
        f"Tested URI : imas:mdsplus?test_validationResultGeneratorUri\n"
        f"Number of tests carried out : 1"
        f"Number of successful tests : 0"
        f"Number of failed tests : 1"
        f"PASSED IDSs:"
        f"FAILED IDSs:"
        f"- IDS core_profiles occurrence 0"
        f"RULE: to/rule.py:dummy_rule_function"
        f"MESSAGE: Optional message"
        f"TRACEBACK: {last_tb}"
        f"NODES COUNT: 3"
        f"NODES: ['a', 'b', 'c']"
        # f"Coverage map:"
    ).replace(
        "\t", ""
    ).replace(
        "\n", ""
    ).replace(
        " ", ""
    )


def test_report_html_generator() -> None:
    # Test report.html generator
    result = IDSValidationResult(
        False,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ["a", "b", "c"]},
        exc=None,
    )
    today = datetime.today()

    uri = "imas:mdsplus?test_validationResultGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    html_result_generator = SummaryReportGenerator([result_collection], today)

    document_style = """
    <style>
        .header {
            width: 100%;
            height: 100%;
            background-color: blue;
            color: white;
            padding: 5px;
        }
        .content {
            padding: 10px;
        }
        body {
            background-color: light-gray;
            font-family: monospace;
            font-size: 16px;
        }
        span[data-validation-successfull="true"]{
            color: green;
        }
        span[data-validation-successfull="false"]{
            color: red;
        }
        li>a {
        display: inline-block;
        margin-left: 10px;
        }
    </style>
    
    """
    # delete white characters from html before assert,
    # to avoid errors connected with html document formatting
    assert (
        html_result_generator.html.replace(" ", "").replace("\t", "")
        == f"""
        <!DOCTYPE html>
        <document>
        <head>
            <title>summary-{today}</title>
            <meta charset="UTF-8"/>
            {document_style}
        </head>
        <body>
        <div class="header">
            <h1>Validation summary</h1><br/>
            {today}<br/>
            Performed tests: 1<br/>
            Failed tests: 1

        </div>
        <div class="content">
            <h3>Passed tests</h3>
            <ol>
            
            </ol>
            <br>
            <h3>Failed tests</h3>
            <ol>
            <li><span data-validation-successfull=false>FAILED: </span>imas:mdsplus?test_validationResultGeneratorUri<br><a href="./imas%3Amdsplus%3Ftest_validationResultGeneratorUri.html">HTML report</a><a href="./imas%3Amdsplus%3Ftest_validationResultGeneratorUri.txt">TXT report</a></li><br/>
            </ol>
        </div>
        </body>
        </document>
    """.replace(
            " ", ""
        ).replace(
            "\t", ""
        )
    )


@pytest.mark.parametrize(
    "expected_result, coverage_dict",
    (
        [False, {}],
        [True, {("core_profiles", 0): CoverageMap(filled=3, visited=3, overlap=3)}],
    ),
)
def test_coverage_dict(expected_result, coverage_dict) -> None:
    # Create a successful assert result, similar to ResultCollector.assert_()
    result = IDSValidationResult(
        True,
        "Optional message",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): ("a", "b", "c")},
        exc=None,
    )
    uri = "imas:mdsplus?test_validationResultGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict=coverage_dict,
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationResultGenerator(result_collection)
    assert ("Coverage map:" in result_generator.txt) == expected_result
