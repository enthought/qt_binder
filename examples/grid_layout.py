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

from traits.api import HasTraits
from traitsui.api import View

from qt_binder.api import Bound
from qt_binder.qt.QtCore import Qt
from qt_binder.raw_widgets import BasicGridLayout, CheckBox, GroupBox, \
    LineEdit, PushButton, SpanGridLayout, VBoxLayout


class Model(HasTraits):
    """ We're just showing off layout, so no model traits.
    """

    def default_traits_view(self):
        traits_view = View(
            Bound(
                VBoxLayout(
                    GroupBox(
                        BasicGridLayout(
                            [u'Always On:', None, LineEdit()],
                            [u'Enableable:',
                             CheckBox(id='field_checkbox'),
                             LineEdit(id='field')],
                            [u'Left:',
                             CheckBox(id='left_checkbox'),
                             (LineEdit(id='left'), Qt.AlignLeft)],
                            [u'Right:',
                             CheckBox(id='right_checkbox'),
                             (LineEdit(id='right'), Qt.AlignRight)],
                        ),
                        title=u'Basic Grid Layout',
                    ),
                    GroupBox(
                        SpanGridLayout(
                            (PushButton(text=u'(0, 0)'), 0, 0),
                            (PushButton(text=u'(0, 1) - (0, 2)'), 0, 1, 1, 2),
                            (PushButton(text=u'(1, 0) - (1, 1)'), 1, 0, 1, 2),
                            (PushButton(
                                text=u'(1, 2)\N{RIGHTWARDS ARROW TO BAR}'),
                             1, 2, Qt.AlignRight),
                            (PushButton(text=u'(2, 0)'), 2, 0),
                            (PushButton(text=u'(2, 2)'), 2, 2),
                        ),
                        title=u'Span Grid Layout',
                    ),
                ),
                'field.enabled << field_checkbox.checked',
                'left.enabled << left_checkbox.checked',
                'right.enabled << right_checkbox.checked',
            ),
            resizable=True,
            title=u'Grid Layouts',
        )
        return traits_view


def main():
    Model().configure_traits()

if __name__ == '__main__':
    main()
