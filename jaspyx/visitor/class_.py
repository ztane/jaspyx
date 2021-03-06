from __future__ import absolute_import, division, print_function
import ast
from jaspyx.ast_util import ast_load, ast_call, ast_store
from jaspyx.context.class_ import ClassContext
from jaspyx.visitor import BaseVisitor
from jaspyx.compat import arguments, FunctionDef


class Class(BaseVisitor):
    def visit_ClassDef(self, node):
        if len(node.bases) > 1:
            raise Exception('Multiple inheritance not supported')

        self.visit(FunctionDef(
            node.name,
            arguments([], None, None, []),
            [
                ast.If(
                    ast.UnaryOp(
                        ast.Not(),
                        ast_call(
                            ast_load('isinstance'),
                            ast_load('this'),
                            ast_load('arguments.callee'),
                        )
                    ),
                    [
                        ast.Return(
                            ast_call(
                                ast_load('new'),
                                ast_load('arguments.callee'),
                                ast_load('arguments'),
                            )
                        )
                    ],
                    []
                ),
                ast.Assign(
                    [ast_store('this.__class__')],
                    ast_load('arguments.callee')
                ),
                ast.Expr(
                    ast_call(
                        ast_load('this.__bind__'),
                        ast_load('this'),
                    ),
                ),
                ast.If(
                    ast.Compare(
                        ast_call(
                            ast_load('type'),
                            ast_load('this.__init__'),
                        ),
                        [ast.IsNot()],
                        [ast.Str('undefined')],
                    ),
                    [
                        ast.Expr(
                            ast_call(
                                ast_load('this.__init__.apply'),
                                ast_load('this'),
                                ast.Subscript(
                                    ast_load('arguments'),
                                    ast.Index(ast.Num(0)),
                                    ast.Load()
                                )
                            )
                        ),
                    ],
                    []
                )
            ],
            []
        ))

        self.push(ClassContext(self.stack[-1], node.name))
        scope = self.stack[-1].scope

        if not node.bases:
            scope.prefix.pop()
            self.visit(
                ast.Assign(
                    [ast_store('prototype')],
                    ast.Dict(
                        [
                            ast.Str('constructor'),
                            ast.Str('__mro__')
                        ],
                        [
                            ast_load(node.name),
                            ast.List([ast_load(node.name)], ast.Load())
                        ]
                    )
                )
            )
            scope.prefix.append('prototype')
            self.visit(
                ast.Assign(
                    [ast_store('__bind__')],
                    FunctionDef(
                        '',
                        arguments([ast_load('self')], None, None, []),
                        [
                            ast.For(
                                ast_store('i'),
                                ast_load('this'),
                                [
                                    ast.If(
                                        ast.Compare(
                                            ast_call(
                                                ast_load('type'),
                                                ast.Subscript(
                                                    ast_load('this'),
                                                    ast.Index(ast_load('i')),
                                                    ast.Load(),
                                                )
                                            ),
                                            [ast.Is()],
                                            [ast.Str('function')]
                                        ),
                                        [
                                            ast.Assign(
                                                [ast.Subscript(
                                                    ast_load('this'),
                                                    ast.Index(ast_load('i')),
                                                    ast.Store(),
                                                )],
                                                ast_call(
                                                    ast.Attribute(
                                                        ast.Subscript(
                                                            ast_load('this'),
                                                            ast.Index(ast_load('i')),
                                                            ast.Load(),
                                                        ),
                                                        'bind',
                                                        ast.Load(),
                                                    ),
                                                    ast_load('self'),
                                                    ast_load('self'),
                                                )
                                            ),
                                        ],
                                        []
                                    )
                                ],
                                []
                            ),
                        ],
                        []
                    )
                )
            )
        else:
            base = node.bases[0]
            self.visit(
                ast.Assign(
                    [ast_store(node.name, 'prototype')],
                    ast_call(
                        FunctionDef(
                            '',
                            arguments([], None, None, []),
                            [
                                ast.Assign(
                                    [ast_store('tmp')],
                                    FunctionDef(
                                        '',
                                        arguments([], None, None, []),
                                        [],
                                        []
                                    )
                                ),
                                ast.Assign(
                                    [ast_store('tmp', 'prototype')],
                                    ast.Attribute(base, 'prototype', ast.Load()),
                                ),
                                ast.Return(
                                    ast_call(
                                        ast_load('new'),
                                        ast_load('tmp'),
                                    )
                                )
                            ],
                            []
                        ),
                    )
                )
            )
            self.visit(
                ast.Assign(
                    [ast_store(node.name, 'prototype.constructor')],
                    ast_load(node.name)
                )
            )
            self.visit(
                ast.Assign(
                    [ast_store(node.name, 'prototype.__base__')],
                    base,
                )
            )
            self.visit(
                ast.Assign(
                    [ast_store(node.name, 'prototype.__mro__')],
                    ast_call(
                        ast_load(node.name, 'prototype.__mro__.concat'),
                        ast_load(node.name),
                    )
                )
            )

        for stmt in node.body:
            self.visit(stmt)

        self.pop()

        if node.decorator_list:
            arg = ast_load(node.name)
            for decorator in node.decorator_list:
                arg = ast_call(decorator, arg)
            self.visit(
                ast.Assign(
                    [ast_store(node.name)],
                    arg
                )
            )
