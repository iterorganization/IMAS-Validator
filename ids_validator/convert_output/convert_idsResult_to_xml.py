import re
from typing import List
from xml.dom import minidom

from ids_validator.validate.result import IDSValidationResult


def create_JUnit_xml(
    ids_validation_result_list: List[IDSValidationResult],
    save_path_file_input_str: str,
) -> None:
    """
    Creation of output file structure in JUnit xml format.

    Args:
        ids_validation_result_list : List of struct_validation_result
        save_path_file_input_str: output file path

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
    testsuites.setAttribute("tests", str(len(ids_validation_result_list)))

    # Get failures tests cpt
    for item in ids_validation_result_list:
        if item.success is False:
            cpt_failure_in_testsuite = cpt_failure_in_testsuite + 1
    testsuites.setAttribute("failures", str(cpt_failure_in_testsuite))
    cpt_failure_in_testsuite = 0

    # Add testsuites to xml
    xml.appendChild(testsuites)

    # Set testsuite balise
    for i in range(len(ids_validation_result_list) - 1):
        if i == 0 or ids_validation_result_list[i].idss.__str__ != ids_tmp:
            ids_tmp = str(ids_validation_result_list[i].idss.__str__)
            testsuite = xml.createElement("testsuite")
            testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
            testsuite.setAttribute("name", ids_tmp)
            testsuite_array.append(testsuite)

    # Set Testcase and append to testsuite
    for testsuite_item in testsuite_array:
        for ids_validation_item in ids_validation_result_list:
            if testsuite_item.getAttribute("name") == ids_validation_item.idss.__str__:
                cpt_test_in_testsuite = cpt_test_in_testsuite + 1
                if ids_validation_item.success is False:
                    cpt_failure_in_testsuite = cpt_failure_in_testsuite + 1
                    testcase = xml.createElement("testcase")
                    testcase.setAttribute(
                        "id",
                        testsuite_item.getAttribute("id")
                        + "."
                        + str(cpt_test_in_testsuite),
                    )
                    testcase.setAttribute("name", ids_validation_item.rule.name)
                    # Add testcase to testSuite
                    testsuite_item.appendChild(testcase)
                    # Create, set failure and append to testcase
                    failure = xml.createElement("failure")
                    failure.setAttribute("message", ids_validation_item.msg)
                    failure.setAttribute("type", "")
                    # failure.appendChild(xml.createTextNode("\n"))
                    failure.appendChild(
                        xml.createTextNode(str(ids_validation_item.tb[-1]))
                    )
                    # failure.appendChild(xml.createTextNode("\n"))
                    # Add failure to testcase
                    testcase.appendChild(failure)
                else:
                    testcase = xml.createElement("testcase")
                    testcase.setAttribute(
                        "id",
                        testsuite_item.getAttribute("id")
                        + "."
                        + str(cpt_test_in_testsuite),
                    )
                    testcase.setAttribute("name", ids_validation_item.rule.name)
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
    xml_str = testsuites.toprettyxml(indent="\t")
    write_xml_and_html_file(xml_str, save_path_file_input_str)


def write_xml_and_html_file(input_str: str, save_path_file_input_str: str) -> None:
    """
    Write file xml, and convert him into html

    Args:
        input_str : content to write
        save_path_file_input_str: output file path

    Return:
    """
    with open(save_path_file_input_str, "w+") as f:
        f.write(input_str)
