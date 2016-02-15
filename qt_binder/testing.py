from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.trait_notifiers import pop_exception_handler, \
    push_exception_handler


class BaseTestWithGui(GuiTestAssistant):

    def setUp(self):
        GuiTestAssistant.setUp(self)
        push_exception_handler(reraise_exceptions=True)

    def tearDown(self):
        pop_exception_handler()
        GuiTestAssistant.tearDown(self)
