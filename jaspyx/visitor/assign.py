from __future__ import absolute_import, division, print_function
import _ast
import ast
from jaspyx.ast_util import ast_call, ast_load, ast_store
from jaspyx.visitor import BaseVisitor


class SimpleAssign(_ast.Assign):
    pass


class Assign(BaseVisitor):
    def build_Assign_Slice(self, target, value):
        args = []
        if target.slice.lower or target.slice.upper:
            args.append(target.slice.lower or ast.Num(0))
        if target.slice.upper:
            args.append(target.slice.upper)

        return ast_call(
            ast.FunctionDef(
                '',
                ast.arguments(
                    [
                        ast_store('t'),
                        ast_store('v'),
                        ast_store('s'),
                        ast_store('e'),
                    ], None, None, []
                ),
                [
                    ast.Assign(
                        [ast_store('s')],
                        ast.IfExp(
                            ast.Compare(
                                ast_call(
                                    ast_load('type'),
                                    ast_load('s')
                                ),
                                [ast.Eq()],
                                [ast.Str('undefined')],
                            ),
                            ast.Num(0),
                            ast.IfExp(
                                ast.Compare(
                                    ast_load('s'),
                                    [ast.Lt()],
                                    [ast.Num(0)],
                                ),
                                ast.BinOp(
                                    ast_load('s'),
                                    ast.Add(),
                                    ast_load('t.length')
                                ),
                                ast_load('s')
                            )
                        )
                    ),
                    ast.Assign(
                        [ast_store('e')],
                        ast.IfExp(
                            ast.Compare(
                                ast_call(
                                    ast_load('type'),
                                    ast_load('e')
                                ),
                                [ast.Eq()],
                                [ast.Str('undefined')],
                            ),
                            ast_load('t.length'),
                            ast.IfExp(
                                ast.Compare(
                                    ast_load('e'),
                                    [ast.Lt()],
                                    [ast.Num(0)],
                                ),
                                ast.BinOp(
                                    ast_load('e'),
                                    ast.Add(),
                                    ast_load('t.length')
                                ),
                                ast_load('e')
                            )
                        )
                    ),
                    ast.Expr(
                        ast_call(
                            ast_load('Array.prototype.splice.apply'),
                            ast_load('t'),
                            ast_call(
                                ast.Attribute(
                                    ast.List([
                                        ast_load('s'),
                                        ast.BinOp(
                                            ast_load('e'),
                                            ast.Sub(),
                                            ast_load('s')
                                        ),
                                    ], ast.Load()),
                                    'concat',
                                    ast.Load(),
                                ),
                                ast_load('v'),
                            )
                        )
                    ),
                    ast.Return(ast_load('v')),
                ],
                []
            ),
            target.value,
            value,
            *args
        )

    def build_Assign_Destructuring(self, targets, value):
        scope = self.stack[-1].scope
        global_scope = scope.get_global_scope()

        assignments = []
        for target, i in zip(targets.elts, range(len(targets.elts))):
            if isinstance(target, _ast.Name):
                if scope.is_global(target.id):
                    global_scope.declare(target.id)
                else:
                    scope.declare(target.id)
                target = ast.Name(target.id, ast.Load())
            assignments.append(
                ast.Assign(
                    [target],
                    ast.Subscript(
                        ast_load('v'),
                        ast.Index(ast.Num(i)),
                        ast.Load()
                    )
                )
            )

        return ast_call(
            ast.FunctionDef(
                '',
                ast.arguments([ast_store('v')], None, None, []),
                assignments + [
                    ast.Return(ast_load('v'))
                ],
                []
            ),
            value
        )

    def visit_SimpleAssign(self, node):
        self.visit(node.targets[0])
        self.output(' = ')
        self.visit(node.value)

    def visit_Assign(self, node):
        body = node.value
        for target in reversed(node.targets):
            if isinstance(target, _ast.List) or isinstance(target, _ast.Tuple):
                body = self.build_Assign_Destructuring(target, body)
            elif isinstance(target, _ast.Subscript) and \
                    isinstance(target.slice, _ast.Slice):
                body = self.build_Assign_Slice(target, body)
            else:
                body = SimpleAssign([target], body)

        self.indent()
        self.visit(body)
        self.finish()
