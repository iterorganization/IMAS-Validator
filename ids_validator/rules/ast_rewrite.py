"""
This file describes the functions for ast rewriting
"""
import ast
from copy import deepcopy
import inspect
from typing import List, Callable


def fix_func(func: Callable, transformer_list: List[ast.NodeTransformer] = []):
    code = inspect.getsource(func)
    # Parse the code into an AST
    tree = ast.parse(code)
    # Apply the transformation
    transformed_tree = deepcopy(tree)
    for transformer in transformer_list:
        transformed_tree = transformer.visit(transformed_tree)
    transformed_tree = ast.fix_missing_locations(transformed_tree)
    # Convert the modified AST back to code
    new_code = compile(transformed_tree, filename="", mode="exec")
    return new_code


class FunctionDefTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.AST):
        return node.body


class AssertTransformer(ast.NodeTransformer):
    def visit_Assert(self, node: ast.AST):
        if node.msg is None:
            args = [node.test]
        else:
            args = [node.test, node.msg]
        replacement = ast.Expr(
            value=ast.Call(
                func=ast.Name(id="assert_", ctx=ast.Load()),
                args=args,
                keywords=[],
            )
        )
        return replacement
