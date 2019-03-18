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

import six

from traits.api import CList, Either, Instance, Int, List, Property, Str, \
    TraitError, Tuple, Unicode, on_trait_change

from .binder import Binder, Composite, NChildren
from .qt import QtCore, QtGui
from .qt.QtCore import Qt
from .type_registry import TypeRegistry


#: The global registry mapping PySide/PyQt types to their Binders.
binder_registry = TypeRegistry()


class Object(Binder):
    qclass = QtCore.QObject


class Widget(Binder):
    qclass = QtGui.QWidget


class DialogButtonBox(Binder):
    qclass = QtGui.QDialogButtonBox


class DesktopWidget(Binder):
    qclass = QtGui.QDesktopWidget


class LineEdit(Binder):
    qclass = QtGui.QLineEdit


class ComboBox(Composite):
    """ Customized to exposed the line-edit widget as a child
    :class:`~.Binder`.
    """
    qclass = QtGui.QComboBox

    lineEdit_class = LineEdit
    lineEdit = Instance(LineEdit)

    @on_trait_change('editable,qobj')
    def _on_editable(self):
        qobj = self.qobj
        if qobj is not None and self.editable:
            self.lineEdit = self.lineEdit_class(qobj=qobj.lineEdit())
            self.lineEdit.configure()
        else:
            if self.lineEdit is not None:
                self.lineEdit.dispose()
            self.lineEdit = None


class FontComboBox(ComboBox):
    qclass = QtGui.QFontComboBox


class CalendarWidget(Binder):
    qclass = QtGui.QCalendarWidget


class PushButton(Binder):
    qclass = QtGui.QPushButton


class CommandLinkButton(Binder):
    qclass = QtGui.QCommandLinkButton


class CheckBox(Binder):
    qclass = QtGui.QCheckBox


class ToolButton(Binder):
    qclass = QtGui.QToolButton


class RadioButton(Binder):
    qclass = QtGui.QRadioButton


class WizardPage(Binder):
    qclass = QtGui.QWizardPage


class Workspace(Binder):
    qclass = QtGui.QWorkspace


class Frame(Binder):
    qclass = QtGui.QFrame


class ToolBox(Binder):
    qclass = QtGui.QToolBox


class TreeView(Binder):
    qclass = QtGui.QTreeView


class TreeWidget(Binder):
    qclass = QtGui.QTreeWidget


class HeaderView(Binder):
    qclass = QtGui.QHeaderView


class TableView(Binder):
    qclass = QtGui.QTableView


class TableWidget(Binder):
    qclass = QtGui.QTableWidget


class ColumnView(Binder):
    qclass = QtGui.QColumnView


class ListView(Binder):
    qclass = QtGui.QListView


class UndoView(Binder):
    qclass = QtGui.QUndoView


class ListWidget(Binder):
    qclass = QtGui.QListWidget


class ScrollArea(Binder):
    qclass = QtGui.QScrollArea


class PlainTextEdit(Binder):
    qclass = QtGui.QPlainTextEdit


class TextEdit(Binder):
    qclass = QtGui.QTextEdit


class TextBrowser(Binder):
    qclass = QtGui.QTextBrowser


class MdiArea(Binder):
    qclass = QtGui.QMdiArea


class GraphicsView(Binder):
    qclass = QtGui.QGraphicsView


class StackedWidget(Binder):
    qclass = QtGui.QStackedWidget


class LCDNumber(Binder):
    qclass = QtGui.QLCDNumber


class Label(Binder):
    qclass = QtGui.QLabel


class ToolBar(Binder):
    qclass = QtGui.QToolBar


class RubberBand(Binder):
    qclass = QtGui.QRubberBand


class TabWidget(Binder):
    qclass = QtGui.QTabWidget


class StatusBar(Binder):
    qclass = QtGui.QStatusBar


class TabBar(Binder):
    qclass = QtGui.QTabBar


class SplitterHandle(Binder):
    qclass = QtGui.QSplitterHandle


class Slider(Binder):
    qclass = QtGui.QSlider


class Dial(Binder):
    qclass = QtGui.QDial


class ScrollBar(Binder):
    qclass = QtGui.QScrollBar


class DateTimeEdit(Binder):
    qclass = QtGui.QDateTimeEdit


class DateEdit(Binder):
    qclass = QtGui.QDateEdit


class TimeEdit(Binder):
    qclass = QtGui.QTimeEdit


class DoubleSpinBox(Binder):
    qclass = QtGui.QDoubleSpinBox


class SpinBox(Binder):
    qclass = QtGui.QSpinBox


class SplashScreen(Binder):
    qclass = QtGui.QSplashScreen


class SizeGrip(Binder):
    qclass = QtGui.QSizeGrip


class Dialog(Binder):
    qclass = QtGui.QDialog


class ColorDialog(Binder):
    qclass = QtGui.QColorDialog


class PrintDialog(Binder):
    qclass = QtGui.QPrintDialog


class PageSetupDialog(Binder):
    qclass = QtGui.QPageSetupDialog


class FileDialog(Binder):
    qclass = QtGui.QFileDialog


class Wizard(Binder):
    qclass = QtGui.QWizard


class ProgressDialog(Binder):
    qclass = QtGui.QProgressDialog


class PrintPreviewDialog(Binder):
    qclass = QtGui.QPrintPreviewDialog


class FontDialog(Binder):
    qclass = QtGui.QFontDialog


class MessageBox(Binder):
    qclass = QtGui.QMessageBox


class InputDialog(Binder):
    qclass = QtGui.QInputDialog


class ErrorMessage(Binder):
    qclass = QtGui.QErrorMessage


class ProgressBar(Binder):
    qclass = QtGui.QProgressBar


class PrintPreviewWidget(Binder):
    qclass = QtGui.QPrintPreviewWidget


class MenuBar(Binder):
    qclass = QtGui.QMenuBar


class Menu(Binder):
    qclass = QtGui.QMenu


class MdiSubWindow(Binder):
    qclass = QtGui.QMdiSubWindow


class MainWindow(Binder):
    qclass = QtGui.QMainWindow


class SingleChild(Composite):
    """ Base class for widgets that typically have just a single child.
    """
    qclass = QtGui.QWidget

    child = Instance(Binder)

    def __init__(self, child=None, **traits):
        super(SingleChild, self).__init__(child=child, **traits)

    def construct(self):
        if self.child is not None:
            self.child.construct()
        super(SingleChild, self).construct()

    def configure(self):
        if self.child is not None:
            if isinstance(self.child.qobj, QtGui.QWidget):
                self.child.qobj.setParent(self.qobj)
            elif isinstance(self.child.qobj, QtGui.QLayout):
                self.qobj.setLayout(self.child.qobj)
        super(SingleChild, self).configure()


class GroupBox(SingleChild):
    qclass = QtGui.QGroupBox


class FocusFrame(Binder):
    qclass = QtGui.QFocusFrame


class DockWidget(Binder):
    qclass = QtGui.QDockWidget


class Layout(NChildren):
    """ Base class for all `QLayouts`.
    """
    qclass = QtGui.QLayout

    def __init__(self, *children, **kwds):
        self.child_binders = list(children)
        super(Layout, self).__init__(**kwds)

    def construct(self):
        """ Build the QLayout.
        """
        for child in self.child_binders:
            child.construct()
        super(Layout, self).construct()


class Splitter(NChildren):
    """ A splitter widget for arbitrary numbers of children.
    """
    qclass = QtGui.QSplitter

    def __init__(self, *children, **kwds):
        self.child_binders = list(children)
        super(Splitter, self).__init__(**kwds)

    def construct(self):
        """ Build the QLayout.
        """
        for child in self.child_binders:
            child.construct()
        super(Layout, self).construct()

    def configure(self):
        super(StackedLayout, self).configure()
        qobj = self.qobj
        for child in self.child_binders:
            widget = child.qobj
            if isinstance(widget, QtGui.QLayout):
                widget = QtGui.QWidget()
                widget.setLayout(child.qobj)
            qobj.addWidget(widget)


class BoxLayout(Layout):
    """ Base class for box layouts.
    """
    qclass = QtGui.QBoxLayout

    def configure(self):
        super(BoxLayout, self).configure()
        qobj = self.qobj
        for child in self.child_binders:
            if isinstance(child.qobj, QtGui.QWidget):
                qobj.addWidget(child.qobj)
            elif isinstance(child.qobj, QtGui.QLayout):
                qobj.addLayout(child.qobj)


class VBoxLayout(BoxLayout):
    """ A vertical layout.
    """
    qclass = QtGui.QVBoxLayout


class HBoxLayout(BoxLayout):
    """ A horizontal layout.
    """
    qclass = QtGui.QHBoxLayout


class StackedLayout(Layout):
    """ A stacked layout.
    """
    qclass = QtGui.QStackedLayout

    def configure(self):
        super(StackedLayout, self).configure()
        qobj = self.qobj
        for child in self.child_binders:
            widget = child.qobj
            if isinstance(widget, QtGui.QLayout):
                widget = QtGui.QWidget()
                widget.setLayout(child.qobj)
            qobj.addWidget(widget)


class BasicGridLayout(Layout):
    """ An explicit grid layout without colspans or rowspans.

    The arguments are equal-length lists of `Binder` widgets, `unicode` labels,
    `(Binder, Qt.Alignment)` tuples, `(unicode, Qt.Alignment)` tuples, or
    `None` for an empty grid cell.
    """
    qclass = QtGui.QGridLayout

    #: List of lists of `Binders`, `unicode` labels, or `None`. Each list
    #: should have the same number of elements (i.e. the number of columns.
    rows = List(CList(Either(
        None,
        Instance(Binder),
        Unicode,
        Tuple(Instance(Binder), Either(Instance(Qt.AlignmentFlag),
                                       Instance(Qt.Alignment))),
        Tuple(Unicode, Either(Instance(Qt.AlignmentFlag),
                              Instance(Qt.Alignment))),
    )))

    #: The child ``Binder`` instances.
    child_binders = Property(List(Instance(Binder)))

    def __init__(self, *rows, **traits):
        rows = list(rows)
        all_ncols = set(len(row) for row in rows)
        if len(all_ncols) > 1:
            # FIXME: Validate on trait assignment, too.
            raise TraitError("Expected the same number of columns: "
                             "got {!r}".format(all_ncols))
        # Skip the Layout.__init__().
        super(Layout, self).__init__(rows=rows, **traits)

    def __repr__(self):
        args = ',\n  '.join(map(repr, self.rows))
        if self.id:
            args += ',\n  id={0.id!r}'.format(self)
        return '{0.__name__}(\n  {1})'.format(type(self), args)

    def configure(self):
        super(Layout, self).configure()
        qobj = self.qobj
        for irow, row in enumerate(self.rows):
            for icol, cell in enumerate(row):
                alignment = Qt.Alignment(0)
                if isinstance(cell, tuple):
                    cell, alignment = cell
                if isinstance(cell, six.string_types):
                    widget = QtGui.QLabel()
                    widget.setText(cell)
                    qobj.addWidget(widget, irow, icol, alignment)
                elif isinstance(cell, Binder):
                    if isinstance(cell.qobj, QtGui.QWidget):
                        qobj.addWidget(cell.qobj, irow, icol, alignment)
                    elif isinstance(cell.qobj, QtGui.QLayout):
                        qobj.addLayout(cell.qobj, irow, icol, alignment)
                    else:
                        raise TypeError("Expected a QWidget or QLayout: "
                                        "got {!r}".format(cell.qobj))
                # Ignore None.

    def _get_child_binders(self):
        children = []
        for row in self.rows:
            for cell in row:
                if isinstance(cell, Binder):
                    children.append(cell)
                elif isinstance(cell, tuple) and isinstance(cell[0], Binder):
                    children.append(cell[0])
        return children


class SpanGridLayout(Layout):
    """ Grid layout with spans.
    """
    qclass = QtGui.QGridLayout

    #: Items to add: `(Binder/unicode, row, col[, rowspan, colspan]
    #: [, alignment])`
    items = List(Either(
        Tuple(Either(Instance(Binder), Unicode), Int, Int),
        Tuple(Either(Instance(Binder), Unicode), Int, Int,
              Instance(Qt.AlignmentFlag)),
        Tuple(Either(Instance(Binder), Unicode), Int, Int, Int, Int),
        Tuple(Either(Instance(Binder), Unicode), Int, Int, Int, Int,
              Instance(Qt.AlignmentFlag)),
    ))

    #: The child ``Binder`` instances.
    child_binders = Property(List(Instance(Binder)))

    def __init__(self, *items, **traits):
        items = list(items)
        # Skip the Layout.__init__().
        super(Layout, self).__init__(items=items, **traits)

    def __repr__(self):
        args = ',\n  '.join(map(repr, self.items))
        if self.id:
            args += ',\n  id={0.id!r}'.format(self)
        return '{0.__name__}(\n  {1})'.format(type(self), args)

    def configure(self):
        super(Layout, self).configure()
        qobj = self.qobj
        for item in self.items:
            cell = item[0]
            if isinstance(cell, six.string_types):
                label = QtGui.QLabel()
                label.setText(cell)
                args = (label,) + item[1:]
            else:  # isiinstance(cell, Binder)
                args = (cell.qobj,) + item[1:]
            if isinstance(args[0], QtGui.QWidget):
                qobj.addWidget(*args)
            elif isinstance(args[0], QtGui.QLayout):
                qobj.addLayout(*args)
            else:
                raise TypeError("Expected a QWidget or QLayout: "
                                "got {!r}".format(args[0]))

    def _get_child_binders(self):
        children = []
        for item in self.items:
            if isinstance(item[0], Binder):
                children.append(item[0])
        return children


class FormLayout(Layout):
    """ Children are (label, widget) pairs.

    The label can be a ``unicode`` string or ``None``. The last item can be
    a single ``Binder`` to take up the whole space.
    """
    qclass = QtGui.QFormLayout

    #: The (label, widget) pairs.
    rows = List(Either(
        Tuple(Either(None, Unicode, Instance(Binder)), Instance(Binder)),
        Instance(Binder),
    ))

    #: The child ``Binder`` instances.
    child_binders = Property(List(Instance(Binder)))

    def __init__(self, *rows, **traits):
        rows = list(rows)
        # Skip the Layout.__init__().
        super(Layout, self).__init__(rows=rows, **traits)

    def configure(self):
        super(Layout, self).configure()
        qobj = self.qobj
        for row in self.rows:
            if isinstance(row, tuple):
                label, widget = row
                widget = widget.qobj
                if isinstance(label, Binder):
                    label = label.qobj
                qobj.addRow(label, widget)
            elif isinstance(row.qobj, QtGui.QWidget):
                qobj.addRow(row.qobj)

    def __repr__(self):
        args = ', '.join(map(repr, self.rows))
        if self.id:
            args += ', id={0.id!r}'.format(self)
        return '{0.__name__}({1})'.format(type(self), args)

    def _get_child_binders(self):
        children = []
        for row in self.rows:
            if isinstance(row, tuple):
                label, widget = row
                if isinstance(label, Binder):
                    children.append(label)
                children.append(widget)
            elif isinstance(row, Binder):
                children.append(row)
        return children


class WithLayout(Composite):
    """ A dumb `QWidget` wrapper with a child `Layout`.

    This is needed in some places where a true `QWidget` is needed instead of
    a `QLayout`.
    """
    qclass = QtGui.QWidget

    child_layout = Instance(Layout)

    def __init__(self, layout, **traits):
        super(WithLayout, self).__init__(child_layout=layout, **traits)

    def configure(self):
        super(WithLayout, self).configure()
        self.qobj.setLayout(self.child_layout.qobj)

    def __repr__(self):
        args = repr(self.child_layout)
        if self.id:
            args += ', id={0.id!r}'.format(self)
        return '{0.__name__}({1})'.format(type(self), args)


class ButtonGroup(Binder):
    """ A group of buttons.

    This is a special `Binder` used in the `button_groups=` keyword to `Bound`.
    `ButtonGroup` is not a widget, so it does not get put into the widget
    hierarchy. It is given the ID strings of the button `Binders` that belong
    to the group.
    """
    qclass = QtGui.QButtonGroup

    #: List of `Binder` ID strings or `(binder_id_str, qt_id_int)`
    button_ids = List(Either(Str, Tuple(Str, Int)))

    def __init__(self, *button_ids, **traits):
        button_ids = list(button_ids)
        super(ButtonGroup, self).__init__(button_ids=button_ids, **traits)

    def add_buttons_from_context(self, context):
        """ Pull out the required buttons from the context and add them.
        """
        for button_id in self.button_ids:
            qt_id = None
            if isinstance(button_id, tuple):
                button_id, qt_id = button_id
            button = context[button_id].qobj
            if qt_id is None:
                self.qobj.addButton(button)
            else:
                self.qobj.addButton(button, qt_id)


# These classes are not intended to be automatically looked up from their Qt
# classes.
_EXCLUDE_FROM_REGISTRY = [
    Composite,
    NChildren,
    SingleChild,
    SpanGridLayout,
    WithLayout,
]


for obj in list(vars().values()):
    if obj in _EXCLUDE_FROM_REGISTRY:
        continue
    if (isinstance(obj, type) and
            issubclass(obj, Binder) and
            obj is not Binder):
        binder_registry.push(obj.qclass, obj)
