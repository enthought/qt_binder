#------------------------------------------------------------------------------
#
#  Copyright (c) 2015, Enthought, Inc.
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

import os
import unittest

from traits.api import HasStrictTraits, Unicode, pop_exception_handler, \
    push_exception_handler
from traitsui.api import View

from ..bound_editor import Bound
from ..qt import QtGui
from ..widgets import TextField, UIFile


def localfile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class TestUiLoader(unittest.TestCase):

    def setUp(self):
        # Start up a QApplication if needed.
        self.app = QtGui.QApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])
        push_exception_handler(reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()

    def test_load_ui_file(self):

        class _Model(HasStrictTraits):
            text = Unicode()

            def default_traits_view(self):
                _ValidatedField = TextField(validator=QtGui.QIntValidator())
                traits_view = View(
                    Bound(
                        UIFile(
                            localfile('form.ui'),
                            overrides={
                                'lineEdit': _ValidatedField,
                            },
                        ),
                        'lineEdit.value := object.text',
                    ),
                )
                return traits_view

        m = _Model()
        ui = m.edit_traits()
        self.assertIsNotNone(ui)


if __name__ == '__main__':
    unittest.main()
