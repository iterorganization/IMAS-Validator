import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from xml.dom import minidom

from ids_validator.validate.result import IDSValidationResult


class ValidationResultGenerator:
    """Class for generating report"""

    @property
    def xml(self) -> str:
        return self._junit_xml

    @property
    def txt(self) -> str:
        return self._junit_txt

    def __init__(self, report_list: List[IDSValidationResult]):
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

    def save_xml(self, file_name: Optional[str] = None) -> None:
        """
        Save generated validation report as JUnit xml file

        Args:
            file_name: Optional[str] - name of file to be saved.
                If not provided, filename is generated based on current date.

        Return:
        """
        if not file_name:
            today = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            dir_path = Path("validate_reports")
            if not dir_path.is_dir():
                dir_path.mkdir(parents=False, exist_ok=False)
            file_name = str(Path.joinpath(dir_path, f"test_result_{today}.xml"))

        with open(file_name, "w+") as f:
            f.write(self._junit_xml)
            print(f"Generated JUnit xml report saved as: {os.path.abspath(file_name)}")

    def save_txt(self, file_name: Optional[str] = None) -> None:
        """
        Save generated validation report summary as plain text file

        Args:
            file_name: Optional[str] - name of file to be saved.
                If not provided, filename is generated based on current date.

        Return:
        """
        if not file_name:
            dir_path = Path("validate_reports")
            if not dir_path.is_dir():
                dir_path.mkdir(parents=False, exist_ok=False)
            today = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            file_name = str(Path.joinpath(dir_path, f"summary_report_{today}.txt"))

        with open(file_name, "w+") as f:
            f.write(self._junit_txt)
            print(
                f"Generated JUnit summary report saved as: {os.path.abspath(file_name)}"
            )
