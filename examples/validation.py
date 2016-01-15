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

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa

from traits.api import Any, Callable, HasTraits, NO_COMPARE, TraitError, \
    Unicode, on_trait_change
from traitsui.api import View

from qt_binder.api import Bound
from qt_binder.qt import QtGui
from qt_binder.raw_widgets import FormLayout, Label
from qt_binder.widgets import TextField, EnumDropDown


class PythonEvalidator(QtGui.QValidator):
    """ A QValidator that uses a Python evaluator function.

    If the function raises a TypeError, ValueError, or TraitError, the input
    will be considered unacceptable. Other errors will propagate.
    """

    def __init__(self, evaluate_func, *args, **kwds):
        self.evaluate_func = evaluate_func
        super(PythonEvalidator, self).__init__(*args, **kwds)

    def validate(self, text, pos):
        try:
            self.evaluate_func(text)
        except (TraitError, TypeError, ValueError):
            status = self.Intermediate
        else:
            status = self.Acceptable
        return status, text, pos


class Model(HasTraits):
    text = Unicode()
    # Make sure we notify every time this is set, even if ``120 == 120.0``.
    value = Any(comparison_mode=NO_COMPARE)
    evaluator_func = Callable(int)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                FormLayout(
                    (u'Text:', TextField(id='field')),
                    (u'Kind:', EnumDropDown(
                        id='combo',
                        values=[
                            (int, u'Integer'),
                            (float, u'Float'),
                        ])),
                    (u'Value:', Label(id='value')),
                    (u'Text:', Label(id='text')),
                ),
                'field.value := object.text',
                'combo.value := object.evaluator_func',
                'field.validator << PythonEvalidator(object.evaluator_func)',
                'value.text << repr(object.value)',
                'text.text << object.text',
                extra_context=dict(PythonEvalidator=PythonEvalidator),
            ),
            resizable=True,
        )
        return traits_view

    @on_trait_change('text,evaluator_func')
    def _update_value(self):
        try:
            value = self.evaluator_func(self.text)
        except (TraitError, TypeError, ValueError):
            value = None
        self.value = value


def main():
    m = Model(text='120')
    m.configure_traits()

if __name__ == '__main__':
    main()
