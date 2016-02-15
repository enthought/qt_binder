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

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.api import HasStrictTraits, Unicode, pop_exception_handler, \
    push_exception_handler
from traitsui.api import View

from ..bound_editor import Bound
from ..qt import QtGui
from ..widgets import TextField, UIFile


def localfile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class TestUiLoader(unittest.TestCase, GuiTestAssistant):

    def setUp(self):
        super(TestUiLoader, self).setUp()
        push_exception_handler(reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()
        super(TestUiLoader, self).tearDown()

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
        tester = ModalDialogTester(lambda: m.edit_traits(kind='livemodal'))

        def _test(tester):
            # Send valid and invalid data through the model to see if it
            # propagates to our overridden widget correctly.
            try:
                w = tester.find_qt_widget(
                    type_=QtGui.QLineEdit,
                    test=lambda w: w.objectName() == u'lineEdit',
                )
                self.assertEqual(m.text, w.text())
                m.text = u'10'
                self.assertEqual(w.text(), u'10')
                self.assertEqual(w.property('valid'), True)
                m.text = u'abc'
                self.assertEqual(w.text(), u'abc')
                self.assertEqual(w.property('valid'), False)
            finally:
                tester.close(accept=True)

        tester.open_and_run(when_opened=_test)


if __name__ == '__main__':
    unittest.main()
