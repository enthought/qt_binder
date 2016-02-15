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

from ..qt import QtCore, QtGui
from ..raw_widgets import BasicGridLayout, GroupBox, HBoxLayout, Label, \
    Object, VBoxLayout, Widget, binder_registry


class TestBoxLayout(unittest.TestCase):

    def setUp(self):
        # Start up a QApplication if needed.
        self.app = QtGui.QApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])

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


class TestGroupBox(unittest.TestCase):

    def test_group_box_can_be_childless(self):
        box = GroupBox()
        box.construct()
        box.configure()
        self.assertIsInstance(box.qobj, QtGui.QGroupBox)

    def test_groupbox_alignment_works(self):
        # PySide has a bug. Ensure that we work around it.
        box = GroupBox()
        box.construct()
        box.configure()
        _ = box.alignment
        box.alignment = QtCore.Qt.AlignLeft
