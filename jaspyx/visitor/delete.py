from __future__ import absolute_import, division, print_function
from jaspyx.visitor import BaseVisitor


class Delete(BaseVisitor):
    def visit_Delete(self, node):
        for target in node.targets:
            self.indent()
            self.output('delete ')
            self.visit(target)
            self.finish()
