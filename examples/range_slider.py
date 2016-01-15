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
""" RangeEditor replacement.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa

from traits.api import HasTraits, Float, Int
from traitsui.api import View

from qt_binder.api import Bound
from qt_binder.qt import QtGui
from qt_binder.raw_widgets import FormLayout
from qt_binder.widgets import FloatSlider, LogSlider, RangeSlider


class Model(HasTraits):
    int_value = Int(0)
    float_value = Float(0.0)
    log_value = Float(1.0)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                FormLayout(
                    (u'Integer:', RangeSlider(
                        id='int_slider',
                        range=(-100, 100))),
                    (u'Float:', RangeSlider(
                        id='float_slider',
                        slider=FloatSlider(),
                        range=(-10.0, 10.0),
                        field_format_func=u'{0:.2f}'.format)),
                    (u'Log:', RangeSlider(
                        id='log_slider',
                        slider=LogSlider(),
                        range=(0.5, 2.0),
                        field_format_func=u'{0:.6f}'.format)),
                    fieldGrowthPolicy=QtGui.QFormLayout.ExpandingFieldsGrow,
                ),
                'int_slider.value := object.int_value',
                'float_slider.value := object.float_value',
                'log_slider.value := object.log_value',
                # Make the labels align nicely by fixing their widths using
                # stylesheets.
                stylesheet=(u'*[binder_class="RangeSlider"] > .QLabel '
                            u'{min-width: 40px; max-width: 40px;}'),
            ),
            resizable=True,
            title=u'Range Sliders',
        )
        return traits_view


def main():
    m = Model()
    m.configure_traits()

if __name__ == '__main__':
    main()
