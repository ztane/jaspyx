from __future__ import absolute_import, division, print_function
import sys
import ast
from operator import attrgetter


PY3 = sys.version_info >= (3,)


if PY3:
    def an_arg(name):
        return arg(arg=name, annotation=None)

    def arguments(*a):
        if a:
            return ast.arguments(a[0], a[1], [], [], a[2], a[3])

        return ast.arguments()

    basestring = str

    def FunctionDef(*a):
        if a:
            return ast.FunctionDef(*(a + ([],)))

        return ast.FunctionDef()

    def get_arg_id(arg):
        if isinstance(arg, ast.Name):
            return arg.id

        return arg.arg


else:
    def an_arg(name):
        return ast.Name(id=name, ctx=ast.Param())

    arguments = ast.arguments
    basestring = basestring
    FunctionDef = ast.FunctionDef
    get_arg_id = attrgetter('id')
