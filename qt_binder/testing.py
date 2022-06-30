# (C) Copyright 2014-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from contextlib import contextmanager

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.trait_notifiers import pop_exception_handler, \
    push_exception_handler


class BaseTestWithGui(GuiTestAssistant):
    """ Base class for testing Binders.

    Starts a Qt event loop and reraise exceptions during traits event handling.
    """

    def setUp(self):
        GuiTestAssistant.setUp(self)
        push_exception_handler(reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()
        GuiTestAssistant.tearDown(self)

    @contextmanager
    def constructed(self, binder):
        """ Take care of the lifecycle of a binder.

        Construct and configure a binder on entry, and dispose it at exit.
        """
        binder.construct()
        try:
            binder.configure()
            yield binder
        finally:
            binder.dispose()
