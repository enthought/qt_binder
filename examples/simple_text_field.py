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

from traits.api import Enum, HasTraits, Unicode
from traitsui.api import Item, View

from qt_binder.api import Bound
from qt_binder.widgets import TextField, EnumDropDown


class Model(HasTraits):
    mode = Enum('auto', 'enter')
    value = Unicode()

    def default_traits_view(self):
        traits_view = View(
            Bound(
                EnumDropDown(
                    values=[('auto', u'Automatic'),
                            ('enter', u'On Enter')]),
                'value := object.mode',
                label=u'Mode:',
            ),
            Item('value', style='readonly'),
            Bound(
                TextField(),
                'mode := object.mode',
                'value := object.value',
                label=u'Text:',
            ),
        )
        return traits_view


def main():
    m = Model(value=u'Something')
    m.configure_traits()

if __name__ == '__main__':
    main()
