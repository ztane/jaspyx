from __future__ import absolute_import, division, print_function
import ast
from jaspyx.visitor import BaseVisitor


class Lambda(BaseVisitor):
    def visit_Lambda(self, node):
        self.visit(ast.FunctionDef(
            '',
            node.args,
            [ast.Return(node.body)],
            []
        ))
