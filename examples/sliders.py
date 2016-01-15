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
""" Three types of sliders, integer, float, and logarithmic.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa

from traits.api import HasTraits, Float, Int
from traitsui.api import View

from qt_binder.api import Bound
from qt_binder.qt import QtGui
from qt_binder.raw_widgets import FormLayout, HBoxLayout, Label
from qt_binder.widgets import IntSlider, FloatSlider, LogSlider


class Model(HasTraits):
    int_value = Int(0)
    float_value = Float(0.0)
    log_value = Float(1.0)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                FormLayout(
                    (u'Integer:', HBoxLayout(
                        IntSlider(id='int_slider', range=(-100, 100)),
                        Label(id='int_text', minimumWidth=50))),
                    (u'Float:', HBoxLayout(
                        FloatSlider(id='float_slider', range=(-10.0, 10.0)),
                        Label(id='float_text', minimumWidth=50))),
                    (u'Log:', HBoxLayout(
                        LogSlider(id='log_slider', range=(0.5, 2.0)),
                        Label(id='log_text', minimumWidth=50))),
                    fieldGrowthPolicy=QtGui.QFormLayout.ExpandingFieldsGrow,
                ),
                'int_slider.value := object.int_value',
                'int_text.text << str(object.int_value)',
                'float_slider.value := object.float_value',
                'float_text.text << u"{:0.2f}".format(object.float_value)',
                'log_slider.value := object.log_value',
                'log_text.text << u"{:0.4f}".format(object.log_value)',
            ),
            resizable=True,
            title=u'Sliders',
        )
        return traits_view


def main():
    m = Model()
    m.configure_traits()

if __name__ == '__main__':
    main()
