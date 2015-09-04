from __future__ import absolute_import, division, print_function
from jaspyx.visitor import BaseVisitor


class Break(BaseVisitor):
    def visit_Break(self, node):
        self.indent()
        self.output('break')
        self.finish()
