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

import unittest

from ..widgets import TextField


class TestTextField(unittest.TestCase):

    def setUp(self):
        super(TestTextField, self).setUp()
        self.clear_trait_changes()

    def clear_trait_changes(self):
        self.trait_changes = []

    def on_trait_change_callback(self, object, name, old, new):
        self.trait_changes.append((object, name, old, new))

    def test_traits(self):
        field = TextField()
        field.on_trait_change(self.on_trait_change_callback, 'value')
        field.value = u''
        self.assertEqual(
            self.trait_changes,
            [(field, 'value', u'', u'')],
        )
        self.clear_trait_changes()
