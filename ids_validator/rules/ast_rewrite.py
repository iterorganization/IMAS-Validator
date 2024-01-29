"""
This file describes the functions for ast rewriting
"""

import ast
from ids_validator.validate.result_collector import ResultCollector
from .data import ValidatorRegistry

from pathlib import Path


def rewrite_assert(code: str, filename: str):
    """
    Rewrite block of code to swap assert statement with given assert function

    Args:
        code: Block of code, most of the time entire file
        filename: Should give the file from which the code was read; pass some
            recognizable value if it wasn’t read from a file ('<string>' is commonly
            used).

    Returns:
        Rewritten block of code
    """
    # Parse the code into an AST
    tree = ast.parse(code)
    # Apply the transformation
    transformed_tree = AssertTransformer().visit(tree)
    transformed_tree = ast.fix_missing_locations(transformed_tree)
    # Convert the modified AST back to code
    new_code = compile(transformed_tree, filename=filename, mode="exec")
    return new_code


class AssertTransformer(ast.NodeTransformer):
    """
    Node transformer that swaps assert statement with given assert function
    """

    def visit_Assert(self, node: ast.AST):
        if node.msg is None:
            args = [node.test]
        else:
            args = [node.test, node.msg]
        replacement = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="assert", ctx=ast.Load()),
                args=args,
                keywords=[],
            )
        )
        return replacement


def run_path(
    rule_path: Path,
    val_registry: ValidatorRegistry,
    result_collector: ResultCollector,
):
    """
    Run the file corresponding to the given path with rewritten assert statements.
    Any found validator tests will be added to the given ValidatorRegistry

    Args:
        rule_path: Path to file that contains ids validators tests
        val_registry: ValidatorRegistry in which the found tests will be placed
        result_collector: ResultCollector where the found tests will deposit their
            results after being run
    """
    file_content = rule_path.read_text()
    new_code = rewrite_assert(file_content, str(rule_path))
    glob = {
        "ids_validator": val_registry.ids_validator,
        "assert": result_collector.assert_,
    }
    exec(new_code, glob)
