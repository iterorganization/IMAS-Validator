import os
from typing import List
from xml.dom import minidom

from ids_validator.validate.result import IDSValidationResult


def create_JUnit_xml(
    ids_validation_result_list: List[IDSValidationResult], file_name: str
) -> None:
    """
    Creation of output file structure in JUnit xml format.

    Args:
        ids_validation_result_list : List of struct_validation_result
        file_name : output file name

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
    cpt_failure_in_testsuite = sum(
        not item.success for item in ids_validation_result_list
    )
    testsuites.setAttribute("failures", str(cpt_failure_in_testsuite))
    cpt_failure_in_testsuite = 0

    # Add testsuites to xml
    xml.appendChild(testsuites)

    # Set testsuite balise
    for i in range(len(ids_validation_result_list) - 1):
        for tuple_item in ids_validation_result_list[i].idss:
            if str(tuple_item[0]) + "-" + str(tuple_item[1]) != ids_tmp:
                ids_tmp = tuple_item[0] + "-" + str(tuple_item[1])
                testsuite = xml.createElement("testsuite")
                testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
                testsuite.setAttribute("name", ids_tmp)
                testsuite_array.append(testsuite)

    # Set Testcase and append to testsuite
    for testsuite_item in testsuite_array:
        for ids_validation_item in ids_validation_result_list:
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
    xml_str = testsuites.toprettyxml(indent="\t")
    write_xml_file(xml_str, file_name)


def write_xml_file(input_str: str, file_name: str) -> None:
    """
    Write file xml

    Args:
        input_str : content to write
        file_name : output file name
    Return:
    """
    file_name_extension = file_name + ".xml"
    with open(file_name_extension, "w+") as f:
        f.write(input_str)
    print("Path file :", os.path.abspath(file_name_extension))
