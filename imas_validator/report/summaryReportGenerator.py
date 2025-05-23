import logging
import os
from typing import List

from imas_validator.validate.result import IDSValidationResultCollection


class SummaryReportGenerator:
    """Class for generating summary report"""

    # class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    @property
    def html(self) -> str:
        return self._html

    def __init__(
        self,
        validation_results: List[IDSValidationResultCollection],
        test_datetime: str,
    ):
        self._validation_results = validation_results
        self._test_datetime: str = test_datetime
        self._html: str = ""
        self.parse()

    def parse(self) -> None:
        self._generate_html()

    def _generate_html(self) -> None:
        """Generates full HTML report summary for validation results
        stored in self._validation_results"""
        num_failed_tests = 0
        failed_tests_list = []
        passed_tests_list = []
        for result_collection in self._validation_results:
            if not all([result.success for result in result_collection.results]):
                failed_tests_list.append(result_collection)
                num_failed_tests += 1
            else:
                passed_tests_list.append(result_collection)

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
            Performed tests: {len(self._validation_results)}<br/>
            Failed tests: {num_failed_tests}

        </div>
        <div class="content">
            <h3>Passed tests</h3>
            <ol>
                {''.join([
                    self._generate_uri_specific_html_element(result_collection)
                    for result_collection in passed_tests_list
                ])}
            </ol>
            <br>
            <h3>Failed tests</h3>
            <ol>
                {''.join([
                    self._generate_uri_specific_html_element(result_collection)
                    for result_collection in failed_tests_list
                ])}
            </ol>
        </div>
        </body>
        </document>
        """  # noqa: E128

    def _generate_uri_specific_html_element(
        self, validation_results: IDSValidationResultCollection
    ) -> str:
        """Returns html code summary generated for specific pair
        (URI, List of Validation results)

        Args:
            validation_results : IDSValidationResultCollection - validation result

        Returns:
            filled html template:
            <li><span data-validation-successfull="false">PASSED/FAILED: </span>{uri}
            <a href="./test_report.html">HTML report</a>
            <a href="./test_report.txt">TXT report</a></li>

        """
        validation_successful: bool = all(
            [result.success for result in validation_results.results]
        )
        PASSED_FAILED_KEYWORD: str = "PASSED" if validation_successful else "FAILED"

        # process filename not to contain slashes, colon or question marks.
        # They are not processed properly by URL bar in browser
        processed_filename = (
            validation_results.imas_uri.replace("/", "|")
            .replace(":", "%3A")
            .replace("?", "%3F")
            .replace("#", "%23")
        )

        return (
            f"<li><span data-validation-successfull="
            f'{"true" if validation_successful else "false"}>'
            f"{PASSED_FAILED_KEYWORD}: </span>"
            f"{validation_results.imas_uri}<br>"
            f'<a href="./{processed_filename}.html">HTML report</a>'
            f'<a href="./{processed_filename}.txt">TXT report</a>'
            f"</li><br/>"
        )

    def save_html(self, file_name: str) -> None:
        """
        Save generated report summary as html file

        Args:
            file_name: str - name of file to be saved.

        Returns:
            None
        """
        with open(file_name, "w+") as file:
            file.write(self.html)
            self.__logger.debug(
                f"Generated summary html report saved as:"
                f" {os.path.abspath(file_name)}"
            )
