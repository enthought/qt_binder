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

from __future__ import print_function

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))  # noqa

from scimath.units.api import unit_parser
from traits.api import Bool, HasStrictTraits, List, Property, Str, Tuple, \
    Unicode, cached_property
from traitsui.api import View, VGroup, Controller

from qt_binder.api import Bound
from qt_binder.widgets import EditableComboBox, TextField
from qt_binder.raw_widgets import CheckBox, HBoxLayout


def unit_string_is_valid(units):
    return unit_parser.parse_unit(units).valid


def units_compatible(u0, u1):
    return (unit_parser.parse_unit(u0).derivation ==
            unit_parser.parse_unit(u1).derivation)


class Model(HasStrictTraits):
    input_units = Str()
    input_units_valid = Property(Bool, depends_on=['input_units'])
    convert_units = Bool(False)
    output_units = Str()
    output_units_valid = Property(Bool, depends_on=['input_units',
                                                    'convert_units',
                                                    'output_units'])

    @cached_property
    def _get_input_units_valid(self):
        return unit_string_is_valid(self.input_units)

    @cached_property
    def _get_output_units_valid(self):
        valid = True
        if self.convert_units:
            valid = unit_string_is_valid(self.output_units)
            if valid:
                valid = units_compatible(self.input_units, self.output_units)
        return valid


class ModelUI(Controller):

    output_units_recommendations = Property(List(Tuple(Str, Unicode)),
                                            depends_on=['model.input_units'])

    all_units_recommendations = List([
        ('m', u'Depth'),
        ('cm', u'Width'),
        ('ms', u'Time'),
        ('none', u'None'),
        ('radians', u'Radians'),
        ('deg', u'Degrees'),
    ])

    def default_traits_view(self):
        traits_view = View(
            VGroup(
                Bound(
                    TextField(id='input_units'),
                    'valid << object.input_units_valid',
                    'value := object.input_units',
                    label=u'Input units:',
                ),
                Bound(
                    HBoxLayout(
                        CheckBox(id='check'),
                        EditableComboBox(id='combo'),
                    ),
                    'combo.lineEdit.valid << object.output_units_valid',
                    'combo.values << handler.output_units_recommendations',
                    'combo.enabled << object.convert_units',
                    'check.checked := object.convert_units',
                    'combo.value >> object.output_units',
                    label=u'Convert units:',
                ),
            ),
            buttons=['OK'],
        )
        return traits_view

    def _get_output_units_recommendations(self):
        recommendations = []
        if unit_string_is_valid(self.model.input_units):
            for unit, description in self.all_units_recommendations:
                if units_compatible(self.model.input_units, unit):
                    recommendations.append(
                        (unit,
                         u'{0} \N{EM DASH} {1}'.format(description, unit)))
        return recommendations


def main():
    m = Model(input_units='m')
    u = ModelUI(m)
    u.configure_traits()
    print('Input: {0.input_units}'.format(m))
    print('Convert: {0.convert_units}'.format(m))
    print('Output: {0.output_units}'.format(m))
    print('Valid: {0.output_units_valid}'.format(m))

if __name__ == '__main__':
    main()
