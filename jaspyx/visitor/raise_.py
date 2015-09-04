from __future__ import absolute_import, division, print_function
from jaspyx.visitor import BaseVisitor


class Raise(BaseVisitor):
    def visit_Raise(self, node):
        if node.inst is not None or node.tback is not None:
            raise ValueError('only one-clause raise is supported')
        self.indent()
        self.output('throw ')
        self.visit(node.type)
        self.finish()
