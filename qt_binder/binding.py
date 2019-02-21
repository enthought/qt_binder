#------------------------------------------------------------------------------
#
#  Copyright (c) 2014-2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from collections import deque
import parser
import re
import symbol
import token

import six

from traits.trait_base import xgetattr, xsetattr

from .binder import Binder


class AnyString(object):
    """ Compare equal to any string type.
    """
    def __eq__(self, other):
        return isinstance(other, six.string_types)

    def __ne__(self, other):
        return not (self == other)


def yield_subtrees(expr):
    """ Preorder traversal of all subtrees in an expression.
    """
    root = parser.expr(expr).totuple()
    stack = deque([root])
    while stack:
        node = stack.popleft()
        children = [child for child in node[1:] if isinstance(child, tuple)]
        stack.extend(children)
        yield node


def find_ext_attrs(expr):
    """ Find all dotted references in the expression.
    """
    ext_attrs = []
    for subtree in yield_subtrees(expr):
        if subtree[1] == (symbol.atom, (token.NAME, AnyString())):
            parts = [subtree[1][1][1]]
            for trailer in subtree[2:]:
                if trailer == (symbol.trailer,
                               (token.DOT, '.'),
                               (token.NAME, AnyString())):
                    parts.append(trailer[2][1])
                else:
                    break
            if len(parts) > 1:
                ext_attrs.append('.'.join(parts))
    return ext_attrs


class _TraitModified(object):
    """ Expose a well-formed trait change handler function with extra data.

    This is a workaround to avoid some problems with defining change handler
    functions inside of other functions. The ``handler()`` method is a proper
    trait change handler.
    """
    def __init__(self, obj, xattr):
        self.obj = obj
        self.xattr = xattr
        self._in_handler = False

    def handler(self, new):
        if not self._in_handler:
            self._in_handler = True
            try:
                xsetattr(self.obj, self.xattr, new)
            finally:
                self._in_handler = False


class _EvaluateExpression(_TraitModified):

    def __init__(self, obj, xattr, context, expression):
        super(_EvaluateExpression, self).__init__(obj, xattr)
        self.context = context
        self.expression = expression

    def handler(self):
        if not self._in_handler:
            self._in_handler = True
            try:
                value = eval(self.expression, self.context)
                xsetattr(self.obj, self.xattr, value)
            finally:
                self._in_handler = False


class Binding(six.with_metaclass(ABCMeta, object)):
    """ Interface for a single binding pair.
    """

    _op_regex = re.compile(r'\s*(=|>>|<<|:=)\s*')

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return '{0.__name__}({1.left!r}, {1.right!r})'.format(type(self), self)

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return (self.left, self.right) == (other.left, other.right)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((type(self), self.left, self.right))

    @classmethod
    def parse(cls, obj):
        """ Parse a binding expression into the right :class:`~.Binding`
        subclass.
        """
        if isinstance(obj, six.string_types):
            left, op, right = cls._op_regex.split(obj, 1)
            return {
                '=': SetOnceTo,
                ':=': SyncedWith,
                '>>': PushedTo,
                '<<': PulledFrom,
            }[op](left, right)
        elif isinstance(obj, Binding):
            return obj
        else:
            raise TypeError("Expected Binding, or binding string; "
                            "got {0!r}".format(obj))

    @abstractmethod
    def bind(self, binder, context):
        """ Perform the binding and store the information needed to undo it.
        """
        raise NotImplementedError()

    @abstractmethod
    def unbind(self):
        """ Undo the binding.
        """
        raise NotImplementedError()

    def _normalize_binder_trait(self, binder, binder_trait, context):
        """ Normalize the Binder and binder trait.
        """
        if '.' in binder_trait:
            head, tail = binder_trait.split('.', 1)
            if isinstance(context.get(head, None), Binder):
                binder = context[head]
                binder_trait = tail
        return binder, binder_trait


class Factory(Binding):
    """ Call the factory to initialize a value.

    The right item of the pair is a callable that will be called once on
    initialization to provide a value for the destination trait.
    """

    def bind(self, binder, context):
        the_binder, binder_trait = self._normalize_binder_trait(
            binder, self.left, context)
        value = self.right()
        xsetattr(the_binder, binder_trait, value)

    def unbind(self):
        pass


class SetOnceTo(Binding):
    """ Evaluate values once.

    The right item of the pair is a string that will be evaluated in the Traits
    UI context once on initialization.

    Mnemonic: ``binder_trait is set once to expression``
    """
    def bind(self, binder, context):
        expression = self.right
        the_binder, binder_trait = self._normalize_binder_trait(
            binder, self.left, context)
        value = eval(expression, context)
        xsetattr(the_binder, binder_trait, value)

    def unbind(self):
        pass

    def __str__(self):
        return '{0.left} = {0.right}'.format(self)


class PulledFrom(Binding):
    """ Listen to traits in the context.

    The right item of each pair is a string representing the extended trait to
    listen to. The first part of this string should be a key into the Traits UI
    context; e.g. to listen to the ``foo`` trait on the model object, use
    ``'object.foo'``. When the ``foo`` trait on the model object fires a trait
    change notification, the ``Binder`` trait will be assigned. The reverse is
    not true: see :class:`~.PushedTo` and :class:`~.SyncedWith` for that
    functionality.

    Mnemonic: ``binder_trait is pulled from context_trait``
    """
    # FIXME: Allow users to explicitly specify a `depends_on` list. This would
    # let users avoid problems with too many dots.
    def bind(self, binder, context):
        the_binder, binder_trait = self._normalize_binder_trait(
            binder, self.left, context)
        rhs = self.right.strip()
        ext_traits = find_ext_attrs(rhs)
        if ext_traits == [rhs]:
            # Simple case of one attribute.
            context_name, xattr = rhs.split('.', 1)
            context_obj = context[context_name]

            handler = _TraitModified(the_binder, binder_trait).handler
            # FIXME: Only check as far down as are HasTraits objects available.
            # We would like to be able to include references to methods on
            # attributes of HasTraits classes.
            # Unfortunately, a valid use case is where a leading object in
            # a true trait chain is None.
            context_obj.on_trait_change(handler, xattr)
            self.pull_handler_data = [(context_obj, handler, xattr)]
            # FIXME: do a better check for an event trait
            try:
                xsetattr(the_binder, binder_trait,
                         xgetattr(context_obj, xattr))
            except AttributeError as e:
                if 'event' not in str(e):
                    raise
        elif ext_traits == []:
            msg = "No traits found in expression: {0!r}".format(rhs)
            raise ValueError(msg)
        else:
            # Expression.
            self.pull_handler_data = []
            handler = _EvaluateExpression(the_binder, binder_trait,
                                          context, rhs).handler
            for ext_trait in ext_traits:
                context_name, xattr = ext_trait.split('.', 1)
                if context_name not in context:
                    # Assume it's a builtin.
                    continue
                context_obj = context[context_name]
                context_obj.on_trait_change(handler, xattr)
                self.pull_handler_data.append((context_obj, handler, xattr))
            # Call the handler once to evaluate and set the value initially.
            handler()

    def unbind(self):
        for context_obj, handler, xattr in self.pull_handler_data:
            context_obj.on_trait_change(handler, xattr, remove=True)

    def __str__(self):
        return '{0.left} << {0.right}'.format(self)


class PushedTo(Binding):
    """ Send trait updates from the ``Binder`` to the model.

    The right item of each pair is a string representing the extended trait to
    assign the value to. The first part of this string should be a key into the
    Traits UI context; e.g. to send to the ``foo`` trait on the model object,
    use ``'object.foo'``. When a change notification for ``binder_trait`` is
    fired, ``object.foo`` will be assigned the sent object. The reverse is not
    true: see :class:`~.PulledFrom` and :class:`~.SyncedWith` for that
    functionality.

    Mnemonic: ``binder_trait is sent to context_trait``
    """
    def bind(self, binder, context):
        ext_trait = self.right
        the_binder, binder_trait = self._normalize_binder_trait(
            binder, self.left, context)
        context_name, xattr = ext_trait.split('.', 1)
        context_obj = context[context_name]

        handler = _TraitModified(context_obj, xattr).handler
        the_binder.on_trait_change(handler, binder_trait)
        self.pushed_handler_data = (the_binder, handler, binder_trait)

    def unbind(self):
        the_binder, handler, binder_trait = self.pushed_handler_data
        the_binder.on_trait_change(handler, binder_trait, remove=True)

    def __str__(self):
        return '{0.left} >> {0.right}'.format(self)


class SyncedWith(PulledFrom, PushedTo):
    """ Bidirectionally synchronize a ``Binder`` trait and a model trait.

    The right item of each pair is a string representing the extended trait to
    synchronize the binder trait with. The first part of this string should be
    a key into the Traits UI context; e.g. to synchronize with the ``foo``
    trait on the model object, use ``'object.foo'``. When a change notification
    for either trait is sent, the value will be assigned to the other. See
    :class:`~.PulledFrom` and :class:`~.PushedTo` for unidirectional
    synchronization.

    Mnemonic: ``binder_trait is synced with context_trait``
    """
    def bind(self, binder, context):
        PulledFrom.bind(self, binder, context)
        PushedTo.bind(self, binder, context)

    def unbind(self):
        PushedTo.unbind(self)
        PulledFrom.unbind(self)

    def __str__(self):
        return '{0.left} := {0.right}'.format(self)
