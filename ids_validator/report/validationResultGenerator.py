import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List
from xml.dom import minidom

from ids_validator.report.utils import (
    CustomResultCollection,
    convert_result_into_custom_collection,
)
from ids_validator.validate.result import IDSValidationResultCollection


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

    def __init__(self, validation_result: IDSValidationResultCollection):
        self._uri: str = validation_result.imas_uri
        self._validation_result = validation_result
        self._junit_xml: str = ""
        self._junit_txt: str = ""
        self.parse(self._validation_result)

    def parse(self, validation_result: IDSValidationResultCollection) -> None:
        """
        Creation of output file structure in JUnit xml format.

        Args:
            validation_result: IDSValidationResultCollection - validation result

        Return:
        """
        self._parse_junit_xml(validation_result)
        self._parse_junit_txt(validation_result)

    def _parse_junit_xml(
        self, validation_result: IDSValidationResultCollection
    ) -> None:
        """
        Creation of output file structure in JUnit xml format.

        Args:
            validation_result: IDSValidationResultCollection - validation result

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
        testsuites.setAttribute("tests", str(len(validation_result.results)))

        # Get failures tests cpt
        cpt_failure_in_testsuite = sum(
            not item.success for item in validation_result.results
        )
        testsuites.setAttribute("failures", str(cpt_failure_in_testsuite))
        cpt_failure_in_testsuite = 0

        # Add testsuites to xml
        xml.appendChild(testsuites)

        # Set testsuite balise
        for report in validation_result.results:
            for tuple_item in report.idss:
                if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                    ids_tmp = tuple_item[0] + "-" + str(tuple_item[1])
                    testsuite = xml.createElement("testsuite")
                    testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
                    testsuite.setAttribute("name", ids_tmp)
                    testsuite_array.append(testsuite)

        # Set Testcase and append to testsuite
        for testsuite_item in testsuite_array:
            for ids_validation_item in validation_result.results:
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

    def _parse_junit_txt(
        self, validation_result: IDSValidationResultCollection
    ) -> None:
        """
        Creation of output file structure in plain text format.

        Args:
            validation_result: IDSValidationResultCollection - validation result

        Return:
            None
        """
        # This function is split into 3 parts:
        # - generate txt report header
        # - generate report body (list od ids-occurrence and result)
        # - generate coverage map

        # --- init variables ---
        self._junit_txt = ""
        txt_report_header = ""
        txt_report_body = ""
        txt_report_coverage_map = ""

        # --------- refactor input data ---------
        custom_result_collection: List[CustomResultCollection] = (
            convert_result_into_custom_collection(validation_result)
        )

        # --------- generate report header ---------
        cpt_test = len(validation_result.results)
        cpt_failure = sum(not item.success for item in validation_result.results)
        cpt_succesful = cpt_test - cpt_failure

        txt_report_header += (
            f"Summary Report : \n"
            f"Tested URI : {validation_result.imas_uri}\n"
            f"Number of tests carried out : {cpt_test}\n"
            f"Number of successful tests : {cpt_succesful}\n"
            f"Number of failed tests : {cpt_failure}\n\n"
        )

        # fill txt report body
        # PASSED tests
        txt_report_body += "PASSED IDSs:\n"
        for custom_result_object in custom_result_collection:
            if all([result.success for result in custom_result_object.result_list]):
                txt_report_body += (
                    f"+ IDS {custom_result_object.ids}"
                    f" occurrence {custom_result_object.occurrence}\n"
                )

        # FAILED tests
        txt_report_body += "\n"
        txt_report_body += "FAILED IDSs:\n"

        for custom_result_object in custom_result_collection:

            # This time we print only failed tests
            if all([result.success for result in custom_result_object.result_list]):
                continue

            txt_report_body += (
                f"- IDS {custom_result_object.ids}"
                f" occurrence {custom_result_object.occurrence}\n"
            )

            for custom_rule_object in custom_result_object.rules:
                txt_report_body += f"\tRULE: {custom_rule_object.rule_name}\n"
                txt_report_body += f"\t\tMESSAGE: {custom_rule_object.message}\n"
                txt_report_body += (
                    f"\t\tTRACEBACK: " f"{custom_rule_object.traceback}\n"
                )
                txt_report_body += (
                    f"\t\tNODES COUNT: " f"{len(custom_rule_object.nodes)}\n"
                )
                txt_report_body += f"\t\tNODES: " f"{custom_rule_object.nodes}" f"\n\n"

        # --------- generate coverage map ---------
        if validation_result.coverage_dict.items():
            txt_report_coverage_map += "\n\nCoverage map:\n"
            for k, v in validation_result.coverage_dict.items():
                txt_report_coverage_map += (
                    f"\t{k[0]}/{k[1]} : filled = {v.filled},"
                    f" visited = {v.visited}, overlap = {v.overlap}\n"
                )

        # --------- put everything into single txt variable ---------
        self._junit_txt = (
            f"{txt_report_header}" f"{txt_report_body}" f"{txt_report_coverage_map}"
        )

    def save_xml(self, file_name: str) -> None:
        """
        Save generated validation report as JUnit xml file

        Args:
            file_name: str - name of file to be saved.

        Return:
        """
        if not file_name:
            file_name = self.gen_default_file_path("test_result", "xml")

        with open(file_name, "w+") as f:
            f.write(self._junit_xml)
            self.__logger.debug(
                f"Generated JUnit report saved as:" f" {os.path.abspath(file_name)}"
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
                f"Generated txt report saved as:" f" {os.path.abspath(file_name)}"
            )

    def gen_default_file_path(self, def_file_name: str, suffix: str) -> str:
        dir_path = Path("validate_reports")
        if not dir_path.is_dir():
            dir_path.mkdir(parents=False, exist_ok=False)
        today = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        file_name = str(dir_path / f"{def_file_name}_{today}.{suffix}")
        return file_name
