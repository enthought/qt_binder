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

from traits.testing.unittest_tools import UnittestTools

from ..qt import QtGui
from ..testing import BaseTestWithGui
from ..widgets import FloatSlider, RangeSlider, TextField


class TestTextField(unittest.TestCase, BaseTestWithGui, UnittestTools):

    def test_traits(self):
        field = TextField()
        self.assertEqual(field.value, u'')
        with self.assertTraitChanges(field, 'value', count=1):
            # The value trait should always fire a notification, even if the
            # value is not different.
            field.value = u''

    def test_validity_in_auto_mode(self):
        with self.constructed(TextField(mode='auto')) as field:
            field.validator = QtGui.QIntValidator(30, 50)

            # Set the text field in an invalid state.
            field.textEdited = '10'
            self.assertEqual(field.value, '10')
            self.assertEqual(field.valid, False)

            # In 'auto' mode, the value and the validity should update
            # automatically even before the user presses "Enter".
            field.textEdited = '40'
            self.assertEqual(field.value, '40')
            self.assertEqual(field.valid, True)


class TestRangeSlider(unittest.TestCase, BaseTestWithGui):

    def test_initialization(self):
        # With a random hash seed, this would fail randomly if we didn't take
        # special care in RangeSlider.__init__()
        inner = FloatSlider()
        outer = RangeSlider(slider=inner, range=(-10.0, 10.0))
        self.assertEqual(inner.range, (-10.0, 10.0))
        self.assertIs(outer.slider, inner)

    def test_field_format_func(self):
        slider = RangeSlider(field_format_func=u'+{0}'.format)
        slider.slider.value = 10
        self.assertEqual(slider.field.text, u'+10')
        slider.value = 20
        self.assertEqual(slider.field.text, u'20')

    def test_field_text_edited(self):
        with self.constructed(RangeSlider()) as slider:
            self.assertEqual(slider.value, 0)
            self.assertEqual(slider.slider.value, 0)
            slider.field.text = '20'
            slider.field.editingFinished = True
            self.assertEqual(slider.value, 20)
            self.assertEqual(slider.slider.value, 20)

    def test_validator_states(self):
        # When the validator is Invalid or Intermediate, the value of the
        # RangeSlider should not change.
        range_slider = RangeSlider(range=(30, 60), value=50)
        with self.constructed(range_slider):
            slider = range_slider.slider
            field = range_slider.field

            self.assertEqual(slider.value, 50)
            self.assertEqual(range_slider.value, 50)

            # State is Intermediate.
            field.text = '1'
            field.editingFinished = True
            self.assertEqual(slider.value, 50)
            self.assertEqual(range_slider.value, 50)

            # State is Invalid.
            field.text = '-1'
            field.editingFinished = True
            self.assertEqual(slider.value, 50)
            self.assertEqual(range_slider.value, 50)
