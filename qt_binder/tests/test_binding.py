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

import unittest

import six

from traits.api import Any, Event, HasTraits, NO_COMPARE, \
    pop_exception_handler, push_exception_handler, Instance

from ..binder import Binder
from ..binding import Binding, Factory, PulledFrom, PushedTo, SetOnceTo, \
    SyncedWith, find_ext_attrs


class DummyBinder(Binder):
    x = Any(comparison_mode=NO_COMPARE)
    child = Instance(HasTraits)


class DummyModel(HasTraits):
    y = Any(10, comparison_mode=NO_COMPARE)
    event = Event()


class TestBinding(unittest.TestCase):

    def setUp(self):
        self.binder = DummyBinder()
        self.model = DummyModel()
        self.blah = DummyBinder()
        self.context = dict(
            object=self.model,
            blah=self.blah,
        )
        push_exception_handler(lambda *args, **kwds: None,
                               reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()

    def test_find_ext_attr(self):
        pairs = [
            ('object', []),  # no dots
            ('object.foo', ['object.foo']),
            ('object.foo.bar', ['object.foo.bar']),
            ('object.foo + 10', ['object.foo']),
            ('object.foo + str(int)', ['object.foo']),
            ('object.foo + str(int)', ['object.foo']),
            ('object.foo + handler.bar', ['object.foo', 'handler.bar']),
            ('object.foo + handler.func(10)', ['object.foo', 'handler.func']),
            ('object.foo + "ohm.m"', ['object.foo']),
            ('object.foo + "ohm.m".format.__name__', ['object.foo']),
            ('(object.foo).text()', ['object.foo']),
        ]
        for expr, ext_attrs in pairs:
            found = find_ext_attrs(expr)
            six.assertCountEqual(self, found, ext_attrs)

    def test_parse_binding(self):
        pairs = [
            ('text = object.text',
             SetOnceTo('text', 'object.text')),
            ('text=object.text',
             SetOnceTo('text', 'object.text')),
            ('checked = object.text == "blah"',
             SetOnceTo('checked', 'object.text == "blah"')),
            ('text = object.func(value="blah")',
             SetOnceTo('text', 'object.func(value="blah")')),
            ('text << object.text',
             PulledFrom('text', 'object.text')),
            ('text<<object.text',
             PulledFrom('text', 'object.text')),
            ('value << object.value << 2',
             PulledFrom('value', 'object.value << 2')),
            ('value << object.value >> 2',
             PulledFrom('value', 'object.value >> 2')),
            ('text >> object.text',
             PushedTo('text', 'object.text')),
            ('text>>object.text',
             PushedTo('text', 'object.text')),
            ('value >> object.value >> 2',
             PushedTo('value', 'object.value >> 2')),
            ('value >> object.value << 2',
             PushedTo('value', 'object.value << 2')),
            ('value := object.value',
             SyncedWith('value', 'object.value')),
            ('value:=object.value',
             SyncedWith('value', 'object.value')),
            ('lineEdit.text << object.text',
             PulledFrom('lineEdit.text', 'object.text')),
        ]
        for text, binding in pairs:
            parsed = Binding.parse(text)
            self.assertEqual(parsed, binding)
            self.assertEqual(hash(parsed), hash(binding))
            self.assertFalse(parsed != binding)
            self.assertFalse(parsed == 10)
            self.assertIs(Binding.parse(binding), binding)
        factory = Factory('text', lambda: 'foo')
        self.assertIs(Binding.parse(factory), factory)
        for bad in [None, ('value', 'object.value')]:
            with self.assertRaises(TypeError):
                Binding.parse(bad)

    def test_set_once_to(self):
        binding = SetOnceTo('x', 'object.y')
        binding.bind(self.binder, self.context)
        self.assertEqual(self.binder.x, 10)
        self.model.y = 20
        self.assertEqual(self.binder.x, 10)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.x, 10)

    def test_factory(self):
        binding = Factory('x', lambda: self.model.y)
        binding.bind(self.binder, self.context)
        self.assertEqual(self.binder.x, 10)
        self.model.y = 20
        self.assertEqual(self.binder.x, 10)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.x, 10)

    def test_pulled_from_trait(self):
        binding = PulledFrom('x', 'object.y')
        binding.bind(self.binder, self.context)
        self.assertEqual(self.binder.x, 10)
        self.model.y = 20
        self.assertEqual(self.binder.x, 20)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.x, 20)

    def test_pulled_from_expression(self):
        binding = PulledFrom('x', 'object.y + 5')
        binding.bind(self.binder, self.context)
        self.assertEqual(self.binder.x, 15)
        self.model.y = 20
        self.assertEqual(self.binder.x, 25)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.x, 25)

    def test_pulled_from_event(self):
        binding = PulledFrom('x', 'object.event')
        binding.bind(self.binder, self.context)
        self.assertIsNone(self.binder.x)
        self.model.event = 10
        self.assertEqual(self.binder.x, 10)
        binding.unbind()
        self.model.event = 20
        self.assertEqual(self.binder.x, 10)

    def test_pushed_to(self):
        binding = PushedTo('x', 'object.y')
        binding.bind(self.binder, self.context)
        # PushedTo does not initialize the model.
        self.assertEqual(self.model.y, 10)
        self.binder.x = 20
        self.assertEqual(self.model.y, 20)
        binding.unbind()
        self.binder.x = 30
        self.assertEqual(self.model.y, 20)

    def test_synced_with(self):
        binding = SyncedWith('x', 'object.y')
        binding.bind(self.binder, self.context)
        self.assertEqual(self.binder.x, 10)
        self.model.y = 20
        self.assertEqual(self.binder.x, 20)
        self.binder.x = 25
        self.assertEqual(self.model.y, 25)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.x, 25)
        self.binder.x = 35
        self.assertEqual(self.model.y, 30)

    def test_child(self):
        self.binder.child = DummyBinder()
        binding = SyncedWith('child.x', 'object.y')
        binding.bind(self.binder, self.context)
        self.assertIsNone(self.binder.x)
        self.assertEqual(self.binder.child.x, 10)
        self.model.y = 20
        self.assertEqual(self.binder.child.x, 20)
        self.binder.child.x = 25
        self.assertEqual(self.model.y, 25)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.binder.child.x, 25)
        self.binder.child.x = 35
        self.assertEqual(self.model.y, 30)

    def test_binder_in_context(self):
        binding = PulledFrom('blah.x', 'object.y')
        binding.bind(self.binder, self.context)
        self.assertEqual(self.blah.x, 10)
        self.model.y = 20
        self.assertEqual(self.blah.x, 20)
        binding.unbind()
        self.model.y = 30
        self.assertEqual(self.blah.x, 20)
