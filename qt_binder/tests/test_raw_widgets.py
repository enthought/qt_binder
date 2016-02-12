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

from ..qt import QtGui
from ..raw_widgets import GroupBox, HBoxLayout, Label, VBoxLayout


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

    def test_group_box_can_be_childless(self):
        box = GroupBox()
        box.construct()
        box.configure()
        self.assertIsInstance(box.qobj, QtGui.QGroupBox)
