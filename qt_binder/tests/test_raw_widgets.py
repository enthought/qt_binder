#------------------------------------------------------------------------------
#
#  Copyright (c) 2014-2016, Enthought, Inc.
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

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.api import pop_exception_handler, push_exception_handler

from ..qt import QtCore, QtGui
from ..raw_widgets import BasicGridLayout, GroupBox, HBoxLayout, Label, \
    LineEdit, Object, VBoxLayout, Widget, binder_registry


class _BaseTestWithGui(GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        push_exception_handler(reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()
        GuiTestAssistant.tearDown(self)


class TestBoxLayout(_BaseTestWithGui, unittest.TestCase):

    def test_configure_nested_layout(self):
        # Regression test for a bug that prevented layouts from being nested.
        nested_layout = VBoxLayout(HBoxLayout(), VBoxLayout())
        nested_layout.construct()
        nested_layout.configure()
        content = [
            nested_layout.qobj.itemAt(idx)
            for idx in range(nested_layout.qobj.count())
        ]
        self.assertEqual(len(content), 2)
        self.assertIsInstance(content[0], QtGui.QHBoxLayout)
        self.assertIsInstance(content[1], QtGui.QVBoxLayout)

    def test_widget_inside_nested_layout_has_parent(self):
        # Regression test for a bug that prevented a widget inside nested
        # layouts from begin displayed.
        label = Label()
        box = GroupBox(VBoxLayout(VBoxLayout(label)))
        box.construct()
        box.configure()
        self.assertIs(label.qobj.parent(), box.qobj)


class TestBinderRegistry(unittest.TestCase):

    def test_lookup_object(self):
        self.assertIs(binder_registry.lookup_by_type(QtCore.QObject),
                      Object)

    def test_lookup_widget(self):
        self.assertIs(binder_registry.lookup_by_type(QtGui.QWidget),
                      Widget)

    def test_lookup_grid_layout(self):
        self.assertIs(binder_registry.lookup_by_type(QtGui.QGridLayout),
                      BasicGridLayout)


class TestGroupBox(_BaseTestWithGui, unittest.TestCase):

    def test_group_box_can_be_childless(self):
        box = GroupBox()
        box.construct()
        try:
            box.configure()
            self.assertIsInstance(box.qobj, QtGui.QGroupBox)
        finally:
            box.dispose()

    def test_groupbox_alignment_works(self):
        # PySide has a bug. Ensure that we work around it.
        box = GroupBox()
        box.construct()
        try:
            box.configure()
            # Test getting.
            box.alignment
            # Test setting.
            box.alignment = QtCore.Qt.AlignLeft
        finally:
            box.dispose()


class TestQLineEdit(_BaseTestWithGui, unittest.TestCase):

    def test_slots_with_arguments_work(self):
        le = LineEdit()
        le.construct()
        try:
            le.configure()
            le.textEdited = u'text'
        finally:
            le.dispose()
