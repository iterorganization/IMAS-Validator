import os
from datetime import datetime
from typing import List
from xml.dom import minidom

from ids_validator.validate.result import IDSValidationResult


class ValidationResultGenerator:
    """Class for generating report"""

    _report_list: List[IDSValidationResult]
    """List of IDSValidationResult"""

    _junit_xml: str
    """content to write in xml file"""

    _junit_txt: str
    """content to wrinte in plain text file"""

    def __init__(self, report_list: List[IDSValidationResult]):
        self._report_list = report_list

    def save_junit_xml(self, file_name: str) -> None:
        """
        Creation of output file structure in JUnit xml format.

        Args:
            file_name : name of file

        Return:
        """

        if file_name is None:
            today = datetime.now().strftime("%Y-%m-%d")
            file_name = f"test_result_{today}"

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
        testsuites.setAttribute("tests", str(len(self._report_list)))

        # Get failures tests cpt
        cpt_failure_in_testsuite = sum(not item.success for item in self._report_list)
        testsuites.setAttribute("failures", str(cpt_failure_in_testsuite))
        cpt_failure_in_testsuite = 0

        # Add testsuites to xml
        xml.appendChild(testsuites)

        # Set testsuite balise
        for i in range(len(self._report_list) - 1):
            for tuple_item in self._report_list[i].idss:
                if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                    ids_tmp = tuple_item[0] + "-" + str(tuple_item[1])
                    testsuite = xml.createElement("testsuite")
                    testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
                    testsuite.setAttribute("name", ids_tmp)
                    testsuite_array.append(testsuite)

        # Set Testcase and append to testsuite
        for testsuite_item in testsuite_array:
            for ids_validation_item in self._report_list:
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
                                "nodes dict", str(ids_validation_item.nodes_dict)
                            )
                            last_tb = str(ids_validation_item.tb[-1])
                            last_tb = last_tb.replace("<", "")
                            last_tb = last_tb.replace(">", "")
                            failure.appendChild(xml.createTextNode(last_tb))
                            # Add failure to testcase
                            testcase.appendChild(failure)
                        else:
                            # Create, set msg and append to testcase
                            if ids_validation_item.msg:
                                msg = xml.createElement("msg")
                                msg.setAttribute("message", ids_validation_item.msg)
                                testcase.appendChild(msg)
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
        self.write_xml_file(file_name)

    def write_xml_file(self, file_name: str) -> None:
        """
        Write file xml

        Args:
            file_name : name of file

        Return:
        """
        file_name_extension = file_name + ".xml"
        with open(file_name_extension, "w+") as f:
            f.write(self._junit_xml)
        print("Path file JUnit xml:", os.path.abspath(file_name_extension))

    def save_junit_txt(self, file_name: str) -> None:
        self._junit_txt = ""
        ids_tmp: str = ""

        if file_name is None:
            today = datetime.now().strftime("%Y-%m-%d")
            file_name = f"summary_report_{today}"
        else:
            file_name = "summary_report_" + file_name

        cpt_test = len(self._report_list)
        cpt_failure = sum(not item.success for item in self._report_list)
        cpt_succesful = cpt_test - cpt_failure

        self._junit_txt += "Summary Report : \n"
        self._junit_txt += "Number of tests carried out : " + str(cpt_test) + "\n"
        self._junit_txt += "Number of successful tests : " + str(cpt_succesful) + "\n"
        self._junit_txt += "Number of failed tests : " + str(cpt_failure) + "\n"
        self._junit_txt += "\n"

        for ids_validation_item in self._report_list:
            for tuple_item in ids_validation_item.idss:
                if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                    self._junit_txt += (
                        "IDS "
                        + str(tuple_item[0])
                        + " occurrence "
                        + str(tuple_item[1])
                        + "\n"
                    )
                    ids_tmp = str(tuple_item[0]) + "-" + str(tuple_item[1])

                if ids_validation_item.success is False:
                    last_tb = str(ids_validation_item.tb[-1])
                    last_tb = last_tb.replace("<", "")
                    last_tb = last_tb.replace(">", "")
                    self._junit_txt += (
                        "\tTest with rule name : "
                        + ids_validation_item.rule.name
                        + ", is failed\n"
                    )
                    self._junit_txt += "\t\tMessage : " + ids_validation_item.msg + "\n"
                    self._junit_txt += "\t\tTraceback : " + last_tb + "\n"
                    self._junit_txt += "\t\tNodes_Dict : " + str(
                        ids_validation_item.nodes_dict
                    )
                else:
                    self._junit_txt += (
                        "\tTest with rule name : "
                        + ids_validation_item.rule.name
                        + ", is successful\n"
                    )

        # Print summary report
        print("===========================")
        print(self._junit_txt)
        print("===========================")
        self.write_plain_text_file(file_name)

    def write_plain_text_file(self, file_name: str) -> None:
        """
        Write plain text file

        Args:
            file_name : name of file

        Return:
        """
        file_name_extension = file_name + ".txt"
        with open(file_name_extension, "w+") as f:
            f.write(self._junit_txt)
        print("Path file summary report:", os.path.abspath(file_name_extension))
