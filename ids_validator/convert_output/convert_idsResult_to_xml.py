import re
from typing import List
from xml.dom import minidom

class struct_validation_result:
    success: bool
    """Whether or not the validation test was successful"""
    msg: str
    """Given message for failed assertion"""
    last_tb: str
    """last frame of traceback frames"""
    ids_name: str
    """ids name"""
    rule_name: str
    """Rule name"""

    def __init__(
        self, success: bool, msg: str, last_tb: str, ids_name: str, rule_name: str
    ) -> None:
        self.success = success
        self.msg = msg
        self.last_tb = last_tb
        self.ids_name = ids_name
        self.rule_name = rule_name

    def to_str(self) -> None:
        print(
            "Success : "
            + str(self.success)
            + ", msg : "
            + self.msg
            + ", last_tb : "
            + self.last_tb
            + ", ids_name : "
            + self.ids_name
            + ", rule_name : "
            + self.rule_name
        )


def parse_output(output_str: str) -> List[struct_validation_result]:
    """
    Make a List of struct_validation_result from output of ids_validator.

    Args:
        output_str: Output ids_validator

    Returns:
        List of struct_validation_result
    """

    struct_validation_result_array = []

    # Get All struct_validation_result
    ids_validation_result_split = output_str.split("IDSValidationResult")
    ids_validation_result_split.pop(0)

    # Create all struct_validation_result and store them into an array
    for item in ids_validation_result_split:
        # Get success
        match_success = re.search(r"success=(\w+)", item)
        if match_success is None:
            raise Exception("No match")
        else:
            if match_success.group(1) == "True":
                success = True
            else:
                success = False
        # Get message
        match_msg = re.search(r"msg='([^']+)'", item)
        if match_msg:
            msg = match_msg.group(1)
        else:
            msg = ""
        # Get last_tb
        match_tb = re.findall(r"<FrameSummary file [^>]+>", item)
        if match_tb:
            last_tb = str(match_tb[-1])
        else:
            last_tb = ""
        # Get ids_name
        match_ids_name = re.search(r"idss=\[\('([^']+)',", item)
        if match_ids_name:
            idss_value = match_ids_name.group(1)
        else:
            idss_value = ""
        # Get rule_name
        rule_name_match = re.search(r"nodes_dict=\{[^}]+?\[([^[\]]+?)\]", item)
        if rule_name_match:
            rule_name = rule_name_match.group(1)
        else:
            rule_name = ""

        result = struct_validation_result(success, msg, last_tb, idss_value, rule_name)
        result.last_tb = result.last_tb.replace("<", "")
        result.last_tb = result.last_tb.replace(">", "")
        result.rule_name = result.rule_name.replace("'", "")
        struct_validation_result_array.append(result)

    return struct_validation_result_array


def create_JUnit_xml(
    ids_validation_result_list: List[struct_validation_result],
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
        if i == 0 or ids_validation_result_list[i].ids_name != ids_tmp:
            ids_tmp = ids_validation_result_list[i].ids_name
            testsuite = xml.createElement("testsuite")
            testsuite.setAttribute("id", "1." + str(len(testsuite_array) + 1))
            testsuite.setAttribute("name", ids_tmp)
            testsuite_array.append(testsuite)

    # Set Testcase and append to testsuite
    for testsuite_item in testsuite_array:
        for ids_validation_item in ids_validation_result_list:
            if testsuite_item.getAttribute("name") == ids_validation_item.ids_name:
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
                    testcase.setAttribute("name", ids_validation_item.rule_name)
                    # Add testcase to testSuite
                    testsuite_item.appendChild(testcase)
                    # Create, set failure and append to testcase
                    failure = xml.createElement("failure")
                    failure.setAttribute("message", ids_validation_item.msg)
                    failure.setAttribute("type", "")
                    # failure.appendChild(xml.createTextNode("\n"))
                    failure.appendChild(xml.createTextNode(ids_validation_item.last_tb))
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
                    testcase.setAttribute("name", ids_validation_item.rule_name)
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
