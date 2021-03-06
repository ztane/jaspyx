from __future__ import absolute_import, division, print_function
import ast
from jaspyx.context.module import ModuleContext
from jaspyx.compat import basestring


class BaseVisitor(ast.NodeVisitor):
    def __init__(self, path, registry, indent=0):
        self.path = path
        self.registry = registry
        self.default_indent = indent
        self.stack = []
        self.module = None

    def push(self, context):
        """
        Push a new context on the stack.

        :param context: An instance of one of the available context from
        the jaspyx.context package.
        """
        self.stack.append(context)

    def pop(self):
        """
        Pop the current context from the stack and append it to the previous
        context as content.
        """
        self.stack[-2].add(self.stack.pop())

    def output(self, s):
        """
        Append literal output to the current context.

        This will also automatically prepend indention.
        """
        self.stack[-1].add(s)

    def indent(self):
        self.output(' ' * (self.stack[-1].indent + 2))

    def finish(self):
        self.output(';\n')

    def group(self, values, prefix='(', infix=' ', infix_node=None, suffix=')'):
        """
        Append a group of values with a configurable prefix, suffix and infix
        to the output buffer. This is used to render a list of AST nodes with
        fixed surroundings.

        :param values: A list of AST nodes.
        :param prefix: Text to prepend before the output.
        :param infix: Text to put between the rendered AST nodes. If
                      infix_node is also specified, infix_node will be
                      surrounded by infix.
        :param infix_node: An AST node to render in between the values.
        :param suffix: Text to append after the output.
        """
        self.output(prefix)
        first = True
        for value in values:
            if not first:
                if infix:
                    self.output(infix)
                if infix_node is not None:
                    self.visit(infix_node)
                    if infix:
                        self.output(infix)
            else:
                first = False
            if isinstance(value, basestring):
                self.output(value)
            else:
                self.visit(value)
        self.output(suffix)

    def block(self, nodes, context=None):
        """
        Process a block of AST nodes and treat all of them as statements. It
        will also control automatic indention and appending semicolons and
        carriage returns to the output. Can optionally push a context on the
        stack before processing and pop it after it's done.

        :param nodes: A list of AST nodes to render.
        :param context: An optional context to push / pop.
        """
        if context is not None:
            self.push(context)

        for node in nodes:
            self.visit(node)

        if context is not None:
            self.pop()

    def visit_Module(self, node):
        """
        Handler for top-level AST nodes. Sets this visitor's module
        attribute to a newly generated ModuleContext.

        :param node: The current AST node being visited.
        """
        self.module = ModuleContext()
        self.module.indent = self.default_indent
        self.push(self.module)
        self.block(node.body)

    def visit_Expr(self, node):
        self.indent()
        self.visit(node.value)
        self.finish()

    def visit_Pass(self, node):
        pass

    def visit_NameConstant(self, node):
        self.visit(ast.Name(str(node.value), ast.Load()))

    def generic_visit(self, node):
        """
        Generic AST node handlers. Raises an exception. This is called by
        ast.NodeVisitor when no suitable visit_<name> method is found.

        :param node: The current AST node being visited.
        """
        raise NotImplementedError('Unsupported AST node %s' % node)
