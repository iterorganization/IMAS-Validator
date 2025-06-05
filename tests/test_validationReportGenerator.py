import traceback
from datetime import datetime
from pathlib import Path
from xml.dom import minidom

import pytest

from imas_validator.report.validationReportGenerator import ValidationReportGenerator
from imas_validator.report.summaryReportGenerator import SummaryReportGenerator
from imas_validator.rules.data import IDSValidationRule
from imas_validator.validate.result import (
    CoverageMap,
    IDSValidationResult,
    IDSValidationResultCollection,
)
from imas_validator.validate_options import ValidateOptions


def dummy_rule_function() -> None:
    pass


def test_error_result_without_affected_nodes() -> None:
    failed_result = IDSValidationResult(
        False,
        "",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        traceback.extract_stack(),
        {("core_profiles", 0): set([""])},
        exc=RuntimeError("Dummy exception"),
    )

    uri = "imas:mdsplus?test_validationReportGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[failed_result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationReportGenerator(result_collection)

    tb = str(failed_result.tb[-1]).replace("<", "").replace(">", "")

    assert result_generator.xml == (
        f"""<testsuites id="1" name="imas_validator" tests="1" failures="1">
	<testsuite id="1.1" name="core_profiles:0">
		<testcase id="1.1.1" name="to/rule.py:dummy_rule_function" classname="core_profiles:0">
			<failure message="" type="" nodes_count="1" nodes="">{tb}

Affected nodes: </failure>
		</testcase>
	</testsuite>
</testsuites>
"""
    )

    last_tb = str(failed_result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")
    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        f"Summary Report : \n"
        f"Tested URI : imas:mdsplus?test_validationReportGeneratorUri\n"
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
        f"NODES: ['']"
        # f"Coverage map:"
    ).replace(
        "\t", ""
    ).replace(
        "\n", ""
    ).replace(
        " ", ""
    )


def test_error_result() -> None:
    # Create an error result, similar to ResultCollector.add_error_result()
    rule_traceback = traceback.extract_stack()
    failed_result = IDSValidationResult(
        False,
        "",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        rule_traceback,
        {("core_profiles", 0): set(["some/node/path"])},
        exc=RuntimeError("Dummy exception"),
    )

    passed_result = IDSValidationResult(
        True,
        "",
        IDSValidationRule(Path("/dummy/path/to/rule.py"), dummy_rule_function, "*"),
        [("core_profiles", 0)],
        rule_traceback,
        {("core_profiles", 0): set(["some/node/path"])},
        exc=RuntimeError("Dummy exception"),
    )

    uri = "imas:mdsplus?test_validationReportGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[failed_result, passed_result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator_failed_first = ValidationReportGenerator(result_collection)

    # make sure order of passed/failed results doesn't matter
    result_collection.results[0], result_collection.results[1] = (
        result_collection.results[1],
        result_collection.results[0],
    )
    result_generator_passed_first = ValidationReportGenerator(result_collection)

    tb = str(failed_result.tb[-1]).replace("<", "").replace(">", "")

    expected_xml = f"""<testsuites id="1" name="imas_validator" tests="2" failures="1">
	<testsuite id="1.1" name="core_profiles:0">
		<testcase id="1.1.1" name="to/rule.py:dummy_rule_function" classname="core_profiles:0">
			<failure message="" type="" nodes_count="1" nodes="some/node/path">{tb}

Affected nodes: some/node/path</failure>
		</testcase>
	</testsuite>
</testsuites>
"""

    assert result_generator_failed_first.xml == expected_xml
    assert result_generator_passed_first.xml == expected_xml

    last_tb = str(failed_result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")

    expected_txt = (
        (
            f"Summary Report : \n"
            f"Tested URI : imas:mdsplus?test_validationReportGeneratorUri\n"
            f"Number of tests carried out : 2\n"
            f"Number of successful tests : 1\n"
            f"Number of failed tests : 1\n\n"
            f"PASSED IDSs:"
            f"FAILED IDSs:"
            f"- IDS core_profiles occurrence 0"
            f"RULE: to/rule.py:dummy_rule_function"
            f"MESSAGE:"
            f"TRACEBACK: {last_tb}"
            f"NODES COUNT: 1"
            f"NODES: ['some/node/path']"
            # f"Coverage map:"
        )
        .replace("\t", "")
        .replace("\n", "")
        .replace(" ", "")
    )

    assert (
        result_generator_failed_first.txt.replace("\t", "")
        .replace("\n", "")
        .replace(" ", "")
        == expected_txt
    )
    assert (
        result_generator_passed_first.txt.replace("\t", "")
        .replace("\n", "")
        .replace(" ", "")
        == expected_txt
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
    uri = "imas:mdsplus?test_validationReportGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationReportGenerator(result_collection)

    assert result_generator.xml == (
        f"""<testsuites id="1" name="imas_validator" tests="1" failures="0">
	<testsuite id="1.1" name="core_profiles:0">
		<testcase id="1.1.1" name="to/rule.py:dummy_rule_function" classname="core_profiles:0"/>
	</testsuite>
</testsuites>
"""
    )

    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        "Summary Report : "
        "Tested URI : imas:mdsplus?test_validationReportGeneratorUri\n"
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
    uri = "imas:mdsplus?test_validationReportGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict={},
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationReportGenerator(result_collection)

    tb = str(result.tb[-1]).replace("<", "").replace(">", "")

    assert result_generator.xml == (
        f"""<testsuites id="1" name="imas_validator" tests="1" failures="1">
	<testsuite id="1.1" name="core_profiles:0">
		<testcase id="1.1.1" name="to/rule.py:dummy_rule_function" classname="core_profiles:0">
			<failure message="Optional message" type="" nodes_count="3" nodes="a b c">{tb}

Affected nodes: a b c</failure>
		</testcase>
	</testsuite>
</testsuites>
"""
    )

    last_tb = str(result.tb[-1])
    last_tb = last_tb.replace("<", "")
    last_tb = last_tb.replace(">", "")

    assert result_generator.txt.replace("\t", "").replace("\n", "").replace(
        " ", ""
    ) == (
        f"Summary Report : "
        f"Tested URI : imas:mdsplus?test_validationReportGeneratorUri\n"
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

    uri = "imas:mdsplus?test_validationReportGeneratorUri"
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
            <li><span data-validation-successfull=false>FAILED: </span>imas:mdsplus?test_validationReportGeneratorUri<br><a href="./imas%3Amdsplus%3Ftest_validationReportGeneratorUri.html">HTML report</a><a href="./imas%3Amdsplus%3Ftest_validationReportGeneratorUri.txt">TXT report</a></li><br/>
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
    uri = "imas:mdsplus?test_validationReportGeneratorUri"
    result_collection = IDSValidationResultCollection(
        results=[result],
        coverage_dict=coverage_dict,
        validate_options=ValidateOptions(),
        imas_uri=uri,
    )
    result_generator = ValidationReportGenerator(result_collection)
    assert ("Coverage map:" in result_generator.txt) == expected_result
