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

from __future__ import division

from math import exp, log
import operator

import six

from traits.api import Any, Callable, Constant, Dict, Enum, Float, Instance, \
    Int, List, NO_COMPARE, Str, Tuple, Undefined, Unicode, on_trait_change

from .binder import Binder, QtDynamicProperty, Rename, Default
from .qt import QtCore, QtGui
from .qt.ui_loader import load_ui
from .raw_widgets import ComboBox, Composite, LineEdit, Slider, binder_registry


INVALID_STYLE_RULE = ("*[valid='false'] "
                      "{ background-color: rgb(255, 192, 192); }")


class TextField(LineEdit):
    """ Simple customization of a LineEdit.

    The widget can be configured to update the model on every text change or
    only when Enter is pressed (or focus leaves). This emulates Traits UI's
    `TextEditor` `auto_set` and `enter_set` configurations.

    If a validator is set, invalid text will cause the background to be red.
    """

    #: The value to sync with the model.
    value = Unicode(comparison_mode=NO_COMPARE)

    #: Whether the `value` updates on every keypress, or when Enter is pressed
    #: (or `focusOut`).
    mode = Enum('auto', 'enter')

    #: Whether or not the current value is valid, for the stylesheet.
    valid = QtDynamicProperty(True)

    def configure(self):
        self.styleSheet = INVALID_STYLE_RULE

    def _update_valid(self, text):
        """ Update the valid trait based on validation of ``text``.
        """
        validator = self.validator
        if validator is not None:
            state, fixed, pos = validator.validate(text, len(text))
            self.valid = (state == validator.Acceptable)

    @on_trait_change('textEdited')
    def _on_textEdited(self, text):
        if (self.mode == 'auto' and
                'value' not in self.loopback_guard):
            with self.loopback_guard('value'):
                self._update_valid(text)
                self.value = text

    @on_trait_change('editingFinished')
    def _on_editingFinished(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.value = self.text

    @on_trait_change('text,validator')
    def _on_text(self):
        self._update_valid(self.text)

    def _value_changed(self, new):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.text = new


class EditableComboBox(ComboBox):
    """ ComboBox with an editable text field.

    We do not do bidirectional synchronization of the value with the model
    since that is typically not required for these use cases.
    """

    lineEdit_class = TextField

    #: The selected value.
    value = Any(Undefined, comparison_mode=NO_COMPARE)

    #: (object, label) pairs.
    values = List(Tuple(Any, Unicode))

    #: Function that is used to compare two objects in the values list for
    #: equality. Defaults to normal Python equality.
    same_as = Callable(operator.eq)

    editable = Constant(True)

    def configure(self):
        self.qobj.setEditable(True)
        self._on_editable()
        super(EditableComboBox, self).configure()

    @on_trait_change('values,values_items,qobj')
    def _update_values(self):
        qobj = self.qobj
        if qobj is not None:
            old_value = self.value
            current_text = qobj.currentText()
            current_index = qobj.currentIndex()
            # Check if the user entered in custom text that should be
            # preserved.
            preserve_text = (current_index == -1 or
                             qobj.itemData(current_index) is None or
                             current_text != qobj.itemText(current_index))
            labels = []
            new_index = -1
            for i, (value, label) in enumerate(self.values):
                if self.same_as(value, old_value):
                    new_index = i
                labels.append(label)

            with self.loopback_guard('value'):
                if qobj.count() > 0:
                    qobj.clear()
                # Items from the list get their index into the values list
                # added as their user data as well. Items added from the text
                # field will have that still be None.
                for i, label in enumerate(labels):
                    qobj.addItem(label, i)
            if preserve_text:
                qobj.setEditText(current_text)
                self.value = current_text
            else:
                qobj.setCurrentIndex(new_index)

    @on_trait_change('currentIndexChanged_int')
    def _on_currentIndexChanged(self, index):
        if index != -1 and 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                values_index = self.qobj.itemData(index)
                if values_index is not None:
                    self.value = self.values[values_index][0]
                else:
                    # Otherwise, it's one of the added values.
                    self.value = self.qobj.itemText(index)

    @on_trait_change('lineEdit:textEdited')
    def _on_textEdited(self, text):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.value = text


class EnumDropDown(ComboBox):
    """ Select from a set of preloaded choices.
    """

    #: The selected value.
    value = Any(Undefined, comparison_mode=NO_COMPARE)

    #: (object, label) pairs.
    values = List(Tuple(Any, Unicode))

    #: Function that is used to compare two objects in the values list for
    #: equality. Defaults to normal Python equality.
    same_as = Callable(operator.eq)

    editable = Constant(False)

    @on_trait_change('values,values_items,qobj')
    def _update_values(self):
        qobj = self.qobj
        if qobj is not None:
            old_value = self.value
            labels = []
            if self.editable:
                new_index = -1
            else:
                new_index = 0
            for i, (value, label) in enumerate(self.values):
                if self.same_as(value, old_value):
                    new_index = i
                labels.append(label)

            if qobj.count() > 0:
                qobj.clear()
            qobj.addItems(labels)
            qobj.setCurrentIndex(new_index)

    @on_trait_change('currentIndexChanged_int')
    def _on_currentIndexChanged(self, index):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.value = self.values[index][0]

    def _value_changed(self, new):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                new_index = -1
                for i, (value, label) in enumerate(self.values):
                    if self.same_as(value, new):
                        new_index = i
                        break
                self.currentIndex = new_index


class UIFile(Composite):
    """ Load a layout from a Qt Designer `.ui` file.

    Widgets and layouts with names that do not start with underscores will be
    added as traits to this :class:`~.Binder`. The :data:`~.binder_registry`
    will be consulted to find the raw :class:`~.Binder` to use for each widget.
    This can be overridden for any named widget using the :attr:`overrides`
    trait.

    In case one wants to let the :class:`~.Binder` to own its widget but just
    use the `.ui` file for layout, use the :attr:`insertions` dictionary. The
    named widget should be a plain `QWidget` in the UI laid out as desired. The
    :class:`~.Binder` will create a new widget as the lone child of this
    widget and take up all of its space.
    """

    qclass = QtGui.QWidget

    #: The .ui file with the layout.
    filename = Str()

    #: Override binders for named widgets.
    overrides = Dict(Str, Instance(Binder))

    #: Insert binders as children of the named QWidgets.
    insertions = Dict(Str, Instance(Binder))

    def __init__(self, filename, **traits):
        super(UIFile, self).__init__(filename=filename, **traits)

    def construct(self, *args, **kwds):
        qobj, to_be_bound = load_ui(self.filename)
        for name in to_be_bound:
            obj = qobj.findChild(QtCore.QObject, name)
            self.add_trait(name, Instance(Binder))
            if name in self.overrides:
                binder = self.overrides[name]
                binder.qobj = obj
            elif name in self.insertions:
                binder = self.insertions[name]
                binder.construct()
                old_layout = obj.layout()
                if old_layout is not None:
                    # Qt hack to replace the layout. We need to ensure that the
                    # old one is truly deleted. Reparent it onto a widget that
                    # we then discard.
                    QtGui.QWidget().setLayout(old_layout)
                layout = QtGui.QVBoxLayout(obj)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(binder.qobj)
            else:
                binder = binder_registry.lookup(obj)()
                binder.qobj = obj
            setattr(self, name, binder)
        self.qobj = qobj


class BaseSlider(Slider):
    """ Base class for the other sliders.

    Mostly for interface-checking and common defaults.
    """

    #: The value to synch with the model.
    value = Any(0)

    #: The inclusive range.
    range = Tuple(Any(0), Any(99))

    #: The underlying Qt value.
    qt_value = Rename('value')

    # The Qt default is vertical for some awful reason.
    orientation = Default(QtCore.Qt.Horizontal)


class IntSlider(BaseSlider):

    #: The value to synch with the model.
    value = Int(0)

    #: The inclusive range.
    range = Tuple(Int(0), Int(99))

    def configure(self):
        # Set the initial values.
        self._range_changed()
        self._value_changed()

    def _range_changed(self):
        if self.qobj is not None:
            self.qobj.setRange(*self.range)
        else:
            minimum, maximum = self.range
            self.trait_set(
                minimum=minimum,
                maximum=maximum,
            )

    def _value_changed(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.qt_value = self.value

    @on_trait_change('qt_value')
    def _on_qt_value(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.value = self.qt_value


class FloatSlider(BaseSlider):

    #: The value to synch with the model.
    value = Float(0.0)

    #: The inclusive range.
    range = Tuple(Float(0.0), Float(1.0))

    #: The number of steps in the range.
    precision = Int(1000)

    def configure(self):
        # Set the initial values.
        self._precision_changed()
        self._value_changed()

    def _precision_changed(self):
        self.maximum = self.precision

    def _range_changed(self):
        self._value_changed()

    def _value_changed(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.qt_value = self._qt_value_from_python(self.value)

    @on_trait_change('qt_value')
    def _on_qt_value(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                self.value = self._python_value_from_qt(self.qt_value)

    def _qt_value_from_python(self, value):
        low, high = self.range
        precision = self.precision
        qt_value = int(round((value - low) * precision / (high - low)))
        qt_value = min(max(qt_value, 0), precision)
        return qt_value

    def _python_value_from_qt(self, qt_value):
        low, high = self.range
        precision = self.precision
        value = qt_value * (high - low) / precision + low
        return value


class LogSlider(FloatSlider):

    #: The inclusive range.
    range = Tuple(Float(1e-2), Float(100.0))

    def _qt_value_from_python(self, value):
        low, high = self.range
        precision = self.precision
        value = max(value, low)
        log_low = log(low)
        log_high = log(high)
        log_value = log(value)
        qt_value = int(round((log_value - log_low) *
                             precision /
                             (log_high - log_low)))
        qt_value = min(max(qt_value, 0), precision)
        return qt_value

    def _python_value_from_qt(self, qt_value):
        low, high = self.range
        precision = self.precision
        log_low = log(low)
        log_high = log(high)
        log_value = qt_value * (log_high - log_low) / precision + log_low
        value = exp(log_value)
        return value


class RangeSlider(Composite):
    """ A slider with labels and a text entry field.

    The root widget is a `QWidget` with a new property
    `binder_class=RangeSlider`. Stylesheets can reference it using the
    selector::

        *[binder_class="RangeSlider"] {...}

    This can be useful for styling the child `QLabels` and `QLineEdit`, for
    example to make a series of `RangeSliders` align.
    """
    qclass = QtGui.QWidget

    #: The value to synch with the model.
    value = Any(0)

    #: The inclusive range.
    range = Tuple(Any(0), Any(99))

    #: The formatting function for the labels.
    label_format_func = Callable(six.text_type)

    #: The formatting function for the text field. This is used only when the
    #: slider is setting the value.
    field_format_func = Callable(six.text_type)

    #: The slider widget.
    slider = Instance(BaseSlider, factory=IntSlider, args=())

    #: The field widget.
    field = Instance(TextField, args=())

    _low_label = Any()
    _high_label = Any()
    _from_text_func = Callable(int)

    def __init__(self, *args, **traits):
        # Make sure that a `slider` argument gets assigned before anything else
        # because it will affect what range can be accepted.
        if 'slider' in traits:
            slider = traits.pop('slider')
            super(RangeSlider, self).__init__()
            self.slider = slider
            self.trait_set(**traits)
        else:
            super(RangeSlider, self).__init__(*args, **traits)

    def construct(self):
        self.slider.construct()
        self.field.construct()
        super(RangeSlider, self).construct()
        self.qobj.setProperty('binder_class', u'RangeSlider')
        layout = QtGui.QHBoxLayout()
        self._low_label = QtGui.QLabel()
        self._low_label.setAlignment(QtCore.Qt.AlignRight)
        self._high_label = QtGui.QLabel()
        self._high_label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self._low_label)
        layout.addWidget(self.slider.qobj)
        layout.addWidget(self._high_label)
        layout.addWidget(self.field.qobj)
        layout.setContentsMargins(0, 0, 0, 0)
        self.qobj.setLayout(layout)

    def configure(self):
        super(RangeSlider, self).configure()
        if isinstance(self.slider, IntSlider):
            # Use an integer validator for the text field.
            self.field.validator = QtGui.QIntValidator()
            self._from_text_func = int
        else:
            self.field.validator = QtGui.QDoubleValidator()
            self._from_text_func = float
        self._update_widgets()

    @on_trait_change('value,range')
    def _update_widgets(self):
        # Update the range then the value because the widgets will just
        # silently reject values out of bounds.
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                value = self.value
                range = self.range
                if self.qobj is not None:
                    self.field.validator.setRange(range[0], range[1])
                    if not isinstance(self.slider, IntSlider):
                        # Note: this assumes that all sliders other than
                        # IntSlider have decimal inputs.
                        self.field.validator.setDecimals(16)
                    self._low_label.setText(self.label_format_func(range[0]))
                    self._high_label.setText(self.label_format_func(range[1]))
                self.field.text = six.text_type(value)
                self.slider.range = range
                self.slider.value = value

    @on_trait_change('slider:value')
    def _on_slider_value(self):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                value = self.slider.value
                self.value = value
                self.field.text = self.field_format_func(value)

    @on_trait_change('field:value')
    def _on_field_text(self, text):
        if 'value' not in self.loopback_guard:
            with self.loopback_guard('value'):
                if self.field.valid:
                    try:
                        value = self._from_text_func(text)
                    except ValueError:
                        pass
                    else:
                        self.value = value
                        self.slider.value = value
