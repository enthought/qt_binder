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

from traits.api import HasStrictTraits, Range, Unicode
from traitsui.api import View

from qt_binder.bound_editor import Bound
from qt_binder.qt import QtGui
from qt_binder.widgets import RangeSlider, TextField, UIFile


def localfile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def format_deg(x):
    return u'{0}\N{DEGREE SIGN}'.format((x + 180) % 360)


class Model(HasStrictTraits):

    text = Unicode(u'123')
    slider_value = Range(-10, 10)
    degrees = Range(0, 359)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                UIFile(
                    localfile('form.ui'),
                    overrides=dict(
                        lineEdit=TextField(validator=QtGui.QIntValidator()),
                    ),
                    insertions=dict(
                        slider=RangeSlider(range=(-10, 10)),
                    ),
                ),
                'lineEdit.value := object.text',
                'dial.value := object.degrees',
                'dial_value.text << format_deg(object.degrees)',
                'slider.value := object.slider_value',
                extra_context=dict(
                    format_deg=format_deg,
                ),
            ),
            resizable=True,
        )
        return traits_view


if __name__ == '__main__':
    m = Model()
    m.configure_traits()
