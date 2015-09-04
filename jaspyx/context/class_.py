from __future__ import absolute_import, division, print_function
from jaspyx.context import Context
from jaspyx.scope import Scope


class ClassContext(Context):
    def __init__(self, parent, name):
        super(ClassContext, self).__init__(parent)
        self.scope = Scope(self.scope)
        self.scope.prefix = parent.scope.prefix + [name, 'prototype']
        self.scope.inherited = False
