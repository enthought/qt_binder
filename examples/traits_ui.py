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

from traits.api import HasTraits, Range
from traitsui.api import Item, View

from qt_binder.api import Bound, TraitsUI
from qt_binder.qt import QtGui
from qt_binder.raw_widgets import FormLayout
from qt_binder.widgets import RangeSlider


class Model(HasTraits):
    low_bound = Range(low=0, high=40)
    high_bound = Range(low=60, high=100)
    x = Range(low='low_bound', high='high_bound')

    def default_traits_view(self):
        traits_view = View(
            Bound(
                FormLayout(
                    (u'Low:',
                     RangeSlider(id='low', range=(0, 40))),
                    (u'High:',
                     RangeSlider(id='high', range=(60, 100))),
                    (u'RangeEditor:',
                     TraitsUI(Item('x'))),
                    fieldGrowthPolicy=QtGui.QFormLayout.ExpandingFieldsGrow,
                ),
                'low.value := object.low_bound',
                'high.value := object.high_bound',
                # Make the labels align nicely by fixing their widths using
                # stylesheets.
                stylesheet=(u'*[binder_class="RangeSlider"] > .QLabel '
                            u'{min-width: 30px; max-width: 30px;}'),
            ),
            resizable=True,
            title=u'Traits UI Editor',
        )
        return traits_view


def main():
    m = Model()
    m.configure_traits()

if __name__ == '__main__':
    main()
