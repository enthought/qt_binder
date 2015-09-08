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

from traits.api import Bool, Instance, pop_exception_handler, \
    push_exception_handler

from ..binder import Binder, Composite, Default, QtDynamicProperty, \
    QtGetterSetter, QtProperty, QtSignal, QtSlot, Rename
from ..qt import QtCore, QtGui, qt_api


class TestBinder(unittest.TestCase):

    def setUp(self):
        # Start up a QApplication if needed.
        self.app = QtGui.QApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])

        push_exception_handler(reraise_exceptions=True)

        # We make a new class here to test that the traits get added only at
        # the right time.
        # WARNING: If anyone instantiates Binder() itself, this subclass will
        # see its added traits, and the test will fail.
        class Object(Binder):
            qclass = QtCore.QObject

            x = QtDynamicProperty(10)

        self.Object = Object

    def tearDown(self):
        pop_exception_handler()

    def test_object_traits(self):
        # No QtTraits made before instantiation.
        previous_traits = {k: v.trait_type
                           for k, v in self.Object.class_traits().items()}
        self.assertNotIn('destroyed', previous_traits)

        self.Object()
        traits = {k: v.trait_type
                  for k, v in self.Object.class_traits().items()}
        self.assertIsInstance(traits['deleteLater'], QtSlot)
        self.assertIsInstance(traits['destroyed'], QtSignal)
        self.assertIsInstance(traits['destroyed_QObject'], QtSignal)
        self.assertIsInstance(traits['objectName'], QtProperty)
        self.assertIsInstance(traits['parent'], QtGetterSetter)
        self.assertIsInstance(traits['x'], QtDynamicProperty)

    def test_dynamic_properties(self):
        obj = self.Object()
        # QtDynamicProperties work correctly before qobj is provided.
        self.assertEqual(obj.x, 10)
        obj.x = 20
        self.assertEqual(obj.x, 20)

        obj.construct()
        qobj = obj.qobj
        obj.configure()

        # QtDynamicProperties work after qobj is provided.
        self.assertEqual(obj.x, 20)
        self.assertEqual(qobj.property('x'), 20)
        obj.x = 30
        self.assertEqual(obj.x, 30)
        self.assertEqual(qobj.property('x'), 30)

        obj.dispose()

    def test_static_properties(self):
        obj = self.Object()
        with self.assertRaises(AttributeError):
            obj.objectName
        obj.objectName = 'object'
        self.assertEqual(obj.objectName, 'object')

        obj.construct()
        qobj = obj.qobj
        obj.configure()

        self.assertEqual(obj.objectName, 'object')
        self.assertEqual(qobj.objectName(), 'object')
        obj.objectName = 'foo'
        self.assertEqual(obj.objectName, 'foo')
        self.assertEqual(qobj.objectName(), 'foo')

        obj.dispose()

    def test_getter_setter(self):
        obj = self.Object()
        with self.assertRaises(AttributeError):
            obj.parent
        parent_qobj = QtCore.QObject()
        other_parent = QtCore.QObject()
        obj.parent = parent_qobj
        self.assertIs(obj.parent, parent_qobj)

        obj.construct()
        qobj = obj.qobj
        obj.configure()

        self.assertIs(obj.parent, parent_qobj)
        self.assertIs(qobj.parent(), parent_qobj)
        obj.parent = other_parent
        self.assertIs(obj.parent, other_parent)
        self.assertIs(qobj.parent(), other_parent)

        obj.dispose()

    def test_slot(self):
        obj = self.Object()
        with self.assertRaises(AttributeError):
            obj.deleteLater

        obj.deleteLater = True
        obj.construct()
        qobj = obj.qobj
        obj.configure()

        self.assertEqual(obj.deleteLater, qobj.deleteLater)
        # FIXME: Test setting afterwards.
        # FIXME: Test other signatures.

        obj.dispose()

    def test_signal(self):
        obj = self.Object()
        with self.assertRaises(AttributeError):
            obj.destroyed

        obj.destroyed = True
        qobj = QtCore.QObject()
        received = []

        def handler():
            received.append(True)

        qobj.destroyed.connect(handler)

        obj.qobj = qobj
        obj.configure()

        self.assertEqual(received, [True])
        obj.destroyed = True
        self.assertEqual(received, [True, True])

        obj.dispose()

    def test_delayed_connection(self):
        obj = self.Object()
        received = []

        def handler(new):
            received.append(new)

        obj.on_trait_change(handler, 'destroyed')
        obj.on_trait_change(handler, 'destroyed_QObject')
        with self.assertRaises(AttributeError):
            obj.destroyed
        with self.assertRaises(AttributeError):
            obj.destroyed_QObject

        obj.construct()
        qobj = obj.qobj
        obj.configure()

        # PyQt4 signal instances are not unique.
        if qt_api == 'pyside':
            self.assertIs(obj.destroyed, qobj.destroyed)
        else:
            # There is no way to check if a PyQt4.QtCore.pyqtBoundSignal is the
            # same as another, and obtaining it from the QObject gets you
            # a different object every time.
            pass

        # Check delayed signal.
        qobj.destroyed[QtCore.QObject].emit(qobj)

        six.assertCountEqual(self, received, [(), qobj])

        # No signal after removal.
        received[:] = []
        obj.on_trait_change(handler, 'destroyed', remove=True)
        obj.on_trait_change(handler, 'destroyed_QObject', remove=True)

        qobj.destroyed[QtCore.QObject].emit(qobj)
        self.assertEqual(received, [])

        # No signal after disposal.
        obj.on_trait_change(handler, 'destroyed')
        obj.on_trait_change(handler, 'destroyed_QObject')
        obj.dispose()
        qobj.destroyed[QtCore.QObject].emit(qobj)
        self.assertEqual(received, [])

    def test_composite(self):
        class LineEdit(Binder):
            qclass = QtGui.QLineEdit

            _configured = Bool(False)
            _disposed = Bool(False)

            def configure(self):
                self._configured = True

            def dispose(self):
                super(LineEdit, self).dispose()
                self._disposed = True

        class ComboBox(Composite):
            qclass = QtGui.QComboBox
            lineEdit = Instance(LineEdit)

            def configure(self):
                self.editable = True
                self.lineEdit = LineEdit(qobj=self.qobj.lineEdit())
                super(ComboBox, self).configure()

        cb = ComboBox()
        cb.construct()
        cb.configure()
        self.assertEqual(list(cb), [cb, cb.lineEdit])
        self.assertEqual(cb.child_binders, [cb.lineEdit])
        self.assertTrue(cb.lineEdit._configured)
        self.assertFalse(cb.lineEdit._disposed)
        cb.dispose()
        self.assertTrue(cb.lineEdit._disposed)

    def test_default_rename(self):
        class Widget(Binder):
            qclass = QtGui.QWidget

            accessibleName = Default(u'blah')
            what_is_this = Rename('whatsThis', default=u'Foo')
            object_name = Rename('objectName')
            the_layout = Rename('layout')
            py_raise = Rename('raise_')

        class SubWidget(Widget):
            pass

        # Test the subclass first so it can't just inherit the traits of the
        # parent class.
        for cls in [SubWidget, Widget]:
            w = cls()
            w.construct()
            self.assertEqual(w.accessibleName, u'blah')
            self.assertEqual(w.qobj.accessibleName(), u'blah')
            self.assertEqual(w.what_is_this, u'Foo')
            self.assertEqual(w.qobj.whatsThis(), u'Foo')
            self.assertEqual(w.object_name, w.qobj.objectName())
            self.assertEqual(w.the_layout, None)
            self.assertEqual(w.py_raise, w.qobj.raise_)
            self.assertNotIn('raise', sorted(w.class_traits()))
            with self.assertRaises(AttributeError):
                w.whatsThis
            with self.assertRaises(AttributeError):
                w.objectName
            with self.assertRaises(AttributeError):
                w.layout
            w.dispose()

            w = cls(accessibleName=u'not-blah', what_is_this=u'Bar')
            w.construct()
            self.assertEqual(w.accessibleName, u'not-blah')
            self.assertEqual(w.qobj.accessibleName(), u'not-blah')
            self.assertEqual(w.what_is_this, u'Bar')
            self.assertEqual(w.qobj.whatsThis(), u'Bar')
            w.dispose()
