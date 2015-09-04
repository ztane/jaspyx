from __future__ import absolute_import, division, print_function
from jaspyx.visitor import BaseVisitor


class Continue(BaseVisitor):
    def visit_Continue(self, node):
        self.indent()
        self.output('continue')
        self.finish()
