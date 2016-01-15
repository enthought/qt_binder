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

from traits.api import HasTraits, List, Any, NO_COMPARE
from traitsui.api import View

from qt_binder.raw_widgets import FormLayout, Label
from qt_binder.widgets import EnumDropDown
from qt_binder.bound_editor import Bound


class Dummy(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '{0}({1.name!r})'.format(type(self), self)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            return self.name == other.name


class Model(HasTraits):

    #: The current list of (object, label) pairs to display in the combobox.
    values = List()

    #: The alternate lists of values.
    alternates = List([
        ([(Dummy('A'), u'A'),
          (Dummy('B'), u'B'),
          (Dummy('B'), u'Second B')],
         u'First List'),
        ([(Dummy('C'), u'C'),
          (Dummy('A'), u'A'),
          (Dummy('D'), u'D')],
         u'Second List'),
    ])

    #: The value selected.
    value = Any(comparison_mode=NO_COMPARE)

    def default_traits_view(self):
        traits_view = View(
            Bound(
                FormLayout(
                    (u'Which List?', EnumDropDown(id='which_list')),
                    (u'Select:', EnumDropDown(id='select')),
                    (u'Value:', Label(id='value_label')),
                ),
                'which_list.values << object.alternates',
                'which_list.value := object.values',
                'select.values << object.values',
                'select.value := object.value',
                'value_label.text << str(object.value)',
            ),
            resizable=True,
        )
        return traits_view

if __name__ == '__main__':
    m = Model()
    m.values = m.alternates[0][0]
    m.value = Dummy('A')
    m.configure_traits()
