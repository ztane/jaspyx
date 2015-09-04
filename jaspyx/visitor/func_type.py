from __future__ import absolute_import, division, print_function
from jaspyx.visitor import BaseVisitor


class FuncType(BaseVisitor):
    def func_type(self, arg):
        self.output('typeof ')
        self.visit(arg)
