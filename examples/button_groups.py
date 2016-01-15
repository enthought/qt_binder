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

from traits.api import Any, HasTraits, NO_COMPARE
from traitsui.api import View

from qt_binder.api import Bound
from qt_binder.raw_widgets import ButtonGroup, FormLayout, GroupBox, Label, \
    PushButton, RadioButton, VBoxLayout


class Model(HasTraits):

    last_clicked_button = Any(comparison_mode=NO_COMPARE)
    last_pressed_button = Any(comparison_mode=NO_COMPARE)
    last_released_button = Any(comparison_mode=NO_COMPARE)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                VBoxLayout(
                    GroupBox(
                        VBoxLayout(
                            PushButton(text=u'Push A', id='push_a'),
                            PushButton(text=u'Push B', id='push_b'),
                            PushButton(text=u'Push C', id='push_c'),
                        ),
                        title=u'Push Buttons',
                    ),
                    GroupBox(
                        VBoxLayout(
                            RadioButton(text=u'Radio A', id='radio_a',
                                        checked=True),
                            RadioButton(text=u'Radio B', id='radio_b'),
                            RadioButton(text=u'Radio C', id='radio_c'),
                        ),
                        title=u'Radio Buttons',
                    ),
                    GroupBox(
                        FormLayout(
                            (u'Clicked:', Label(id='clicked')),
                            (u'Pressed:', Label(id='pressed')),
                            (u'Released:', Label(id='released')),
                        ),
                        title=u'Events',
                    ),
                ),
                ('push_buttons.buttonClicked_QAbstractButton >> '
                 'object.last_clicked_button'),
                ('push_buttons.buttonPressed_QAbstractButton >> '
                 'object.last_pressed_button'),
                ('push_buttons.buttonReleased_QAbstractButton >> '
                 'object.last_released_button'),
                ('radio_buttons.buttonClicked_QAbstractButton >> '
                 'object.last_clicked_button'),
                ('radio_buttons.buttonPressed_QAbstractButton >> '
                 'object.last_pressed_button'),
                ('radio_buttons.buttonReleased_QAbstractButton >> '
                 'object.last_released_button'),
                ('clicked.text << (object.last_clicked_button).text() '
                 'if object.last_clicked_button else u""'),
                ('pressed.text << (object.last_pressed_button).text() '
                 'if object.last_pressed_button else u""'),
                ('released.text << (object.last_released_button).text() '
                 'if object.last_released_button else u""'),
                button_groups=dict(
                    push_buttons=ButtonGroup('push_a', 'push_b', 'push_c'),
                    radio_buttons=ButtonGroup('radio_a', 'radio_b', 'radio_c',
                                              exclusive=True),
                ),
            ),
            resizable=True,
            width=200,
            title=u'Button Groups',
        )
        return traits_view


def main():
    Model().configure_traits()

if __name__ == '__main__':
    main()
