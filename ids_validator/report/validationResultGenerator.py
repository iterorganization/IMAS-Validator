import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List
from xml.dom import minidom

from ids_validator.validate.result import IDSValidationResult


class ValidationResultGenerator:
    """Class for generating report"""

    # class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    @property
    def xml(self) -> str:
        return self._junit_xml

    @property
    def txt(self) -> str:
        return self._junit_txt

    def __init__(self, uri: str, report_list: List[IDSValidationResult]):
        self._uri: str = uri
        self._report_list = report_list
        self._junit_xml: str = ""
        self._junit_txt: str = ""
        self.parse(self._report_list)

    def parse(self, report_list: List[IDSValidationResult]) -> None:
        """
        Creation of output file structure in JUnit xml format.

        Args:
            report_list: List[IDSValidationResult] - list of validation report results

        Return:
        """
        self._parse_junit_xml(report_list)
        self._parse_junit_txt(report_list)

    def _parse_junit_xml(self, report_list: List[IDSValidationResult]) -> None:
        """
        Creation of output file structure in JUnit xml format.

        Args:
            report_list: List[IDSValidationResult] - list of validation report results

        Return:
        """

        cpt_test_in_testsuite: int = 0
        cpt_failure_in_testsuite: int = 0
        ids_tmp: str = ""
        testsuite_array: List[minidom.Element] = []

        # Create minidom Document in JUnit xml format
        xml = minidom.Document()

        # Set testsuites balise
        testsuites = xml.createElement("testsuites")
        testsuites.setAttribute("id", "1")
        testsuites.setAttribute("name", "ids_validator")
        testsuites.setAttribute("tests", str(len(report_list)))

        # Get failures tests cpt
        cpt_failure_in_testsuite = sum(not item.success for item in report_list)
        testsuites.setAttribute("failures", str(cpt_failure_in_testsuite))
        cpt_failure_in_testsuite = 0

        # Add testsuites to xml
        xml.appendChild(testsuites)

        # Set testsuite balise
        for report in report_list:
            for tuple_item in report.idss:
                if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                    ids_tmp = tuple_item[0] + "-" + str(tuple_item[1])
                    testsuite = xml.createElement("testsuite")
                    testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
                    testsuite.setAttribute("name", ids_tmp)
                    testsuite_array.append(testsuite)

        # Set Testcase and append to testsuite
        for testsuite_item in testsuite_array:
            for ids_validation_item in report_list:
                for tuple_item in ids_validation_item.idss:
                    if testsuite_item.getAttribute("name") == tuple_item[0] + "-" + str(
                        tuple_item[1]
                    ):
                        cpt_test_in_testsuite = cpt_test_in_testsuite + 1
                        testcase = xml.createElement("testcase")
                        testcase.setAttribute(
                            "id",
                            testsuite_item.getAttribute("id")
                            + "."
                            + str(cpt_test_in_testsuite),
                        )
                        testcase.setAttribute("name", ids_validation_item.rule.name)
                        if ids_validation_item.success is False:
                            cpt_failure_in_testsuite = cpt_failure_in_testsuite + 1
                            # Add testcase to testSuite
                            testsuite_item.appendChild(testcase)
                            # Create, set failure and append to testcase
                            failure = xml.createElement("failure")
                            failure.setAttribute("message", ids_validation_item.msg)
                            failure.setAttribute("type", "")
                            failure.setAttribute(
                                "nodes_dict", str(ids_validation_item.nodes_dict)
                            )
                            tb = "\n".join(ids_validation_item.tb.format())
                            failure.appendChild(xml.createTextNode(tb))
                            # Add failure to testcase
                            testcase.appendChild(failure)
                        else:
                            # Add testcase to testSuite
                            testsuite_item.appendChild(testcase)
            testsuite_item.setAttribute("tests", str(cpt_test_in_testsuite))
            testsuite_item.setAttribute("failures", str(cpt_failure_in_testsuite))
            cpt_test_in_testsuite = 0
            cpt_failure_in_testsuite = 0

        # Append testsuite to xml
        for item_element in testsuite_array:
            testsuites.appendChild(item_element)

        # Write xml file
        self._junit_xml = testsuites.toprettyxml(indent="\t")

    def _parse_junit_txt(self, report_list: List[IDSValidationResult]) -> None:
        """
        Creation of output file structure in plain text format.

        Args:
            report_list: List[IDSValidationResult] - list of validation report results

        Return:
        """

        self._junit_txt = ""
        ids_tmp: str = ""

        cpt_test = len(report_list)
        cpt_failure = sum(not item.success for item in report_list)
        cpt_succesful = cpt_test - cpt_failure

        self._junit_txt = (
            f"Summary Report : \n"
            f"Tested URI : {self._uri}\n"
            f"Number of tests carried out : {str(cpt_test)}\n"
            f"Number of successful tests : {str(cpt_succesful)}\n"
            f"Number of failed tests : {str(cpt_failure)}\n\n"
        )

        for ids_validation_item in report_list:
            for tuple_item in ids_validation_item.idss:
                if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                    self._junit_txt += (
                        f"IDS {str(tuple_item[0])} occurrence {str(tuple_item[1])}\n"
                    )
                    ids_tmp = str(tuple_item[0]) + "-" + str(tuple_item[1])

                if ids_validation_item.success is False:
                    last_tb = str(ids_validation_item.tb[-1])
                    last_tb = last_tb.replace("<", "")
                    last_tb = last_tb.replace(">", "")
                    self._junit_txt += (
                        f"\nTest with rule name : "
                        f"{ids_validation_item.rule.name}, failed\n"
                    )
                    self._junit_txt += f"\t\tMessage : {ids_validation_item.msg}\n"
                    self._junit_txt += f"\t\tTraceback : {last_tb}\n"
                    self._junit_txt += (
                        f"\t\tNodes_Dict : {ids_validation_item.nodes_dict}\n"
                    )
                else:
                    self._junit_txt += (
                        f"\tTest with rule name : "
                        f"{ids_validation_item.rule.name}, was successful\n"
                    )

    def save_xml(self, file_name: str, verbose: bool = False) -> None:
        """
        Save generated validation report as JUnit xml file

        Args:
            file_name: str - name of file to be saved.
            verbose: bool - determines if function will print INFO message

        Return:
        """
        if not file_name:
            file_name = self.gen_default_file_path("test_result", "xml")

        with open(file_name, "w+") as f:
            f.write(self._junit_xml)
            if verbose:
                print(
                    f"Generated JUnit xml report saved as:"
                    f" {os.path.abspath(file_name)}"
                )

    def save_txt(self, file_name: str) -> None:
        """
        Save generated validation report summary as plain text file

        Args:
            file_name: str - name of file to be saved.

        Return:
        """
        if not file_name:
            file_name = self.gen_default_file_path("summary_report", "txt")

        with open(file_name, "w+") as f:
            f.write(self._junit_txt)
            self.__logger.debug(
                f"Generated JUnit summary report saved as:"
                f" {os.path.abspath(file_name)}"
            )

    def gen_default_file_path(self, def_file_name: str, suffix: str) -> str:
        dir_path = Path("validate_reports")
        if not dir_path.is_dir():
            dir_path.mkdir(parents=False, exist_ok=False)
        today = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        file_name = str(dir_path / f"{def_file_name}_{today}.{suffix}")
        return file_name


class SummaryReportGenerator:
    """Class for generating summary report"""

    # class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    @property
    def html(self) -> str:
        return self._html

    def __init__(
        self, result_dict: dict[str, List[IDSValidationResult]], test_datetime: str
    ):
        self._result_dict = result_dict
        self._test_datetime: str = test_datetime
        self._html: str = ""
        self.parse()

    def parse(self) -> None:
        self._generate_html()

    def _generate_html(self) -> None:
        """ """
        num_failed_tests = 0
        failed_tests_dict = {}
        passed_tests_dict = {}
        for uri, result_list in self._result_dict.items():
            if not all([result.success for result in result_list]):
                failed_tests_dict[uri] = result_list
                num_failed_tests += 1
            else:
                passed_tests_dict[uri] = result_list

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
        self._html = f"""
        <!DOCTYPE html>
        <document>
        <head>
            <title>summary-{self._test_datetime}</title>
            <meta charset="UTF-8"/>
            {document_style}
        </head>
        <body>
        <div class="header">
            <h1>Validation summary</h1><br/>
            {self._test_datetime}<br/>
            Performed tests: {len(self._result_dict)}<br/>
            Failed tests: {num_failed_tests}

        </div>
        <div class="content">
            <h3>Passed tests</h3>
            <ol>
            {''.join([self._generate_uri_specific_html_element(uri, result_list)
                      for uri, result_list in passed_tests_dict.items()])}
            </ol>
            <br>
            <h3>Failed tests</h3>
            <ol>
            {''.join([self._generate_uri_specific_html_element(uri, result_list)
                      for uri, result_list in failed_tests_dict.items()])}
            </ol>
        </div>
        </body>
        </document>
        """

    def _generate_uri_specific_html_element(
        self, uri: str, result_list: List[IDSValidationResult]
    ) -> str:
        """
        Returns html code summary generated for specific pair URI
         - List of Validation results

        Args:
            uri : str - uri to be put in html code
            result_list : List[IDSValidationResult]
             - list of validation results specific for given uri

        Returns:
            filled html temlpate
            if validation was successful:
            <li><span data-validation-successfull="true">PASSED: </span>{uri}</li>

            else:
            <li><span data-validation-successfull="false">FAILED: </span>{uri}
            <a href="./test_report.xml">Go to JUnit report</a>
            <a href="./test_report.txt">Go to txt report</a></li>

        """
        validation_successfull: bool = all([result.success for result in result_list])
        if validation_successfull:
            return (
                f'<li><span data-validation-successfull="true">'
                f"PASSED: </span>{uri}</li>"
            )

        # process filename not to contain slashes, colon or question marks.
        # They are not processed properly by URL bar in browser
        processed_filename = (
            uri.replace("/", "|").replace(":", "%3A").replace("?", "%3F")
        )

        return (
            f'<li><span data-validation-successfull="false">FAILED: </span>{uri}<br>'
            f'<a href="./{processed_filename}.xml">Go to JUnit report</a>'
            f'<a href="./{processed_filename}.txt">Go to txt report</a>'
            f"</li><br/>"
        )

    def save_html(self, file_path: str) -> None:
        """
        Save generated report summary as html file

        Args:
            file_name: str - name of file to be saved.
        """
        with open(file_path, "w+") as file:
            file.write(self.html)
            self.__logger.debug(
                f"Generated summary html report saved as:"
                f" {os.path.abspath(file_path)}"
            )
