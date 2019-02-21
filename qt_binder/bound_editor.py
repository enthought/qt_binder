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

from traits.api import Any, Callable, Dict, Either, HasPrivateTraits, \
    Instance, List, Str, Undefined
from traitsui.editor_factory import EditorFactory
from traitsui.item import Item
from traitsui.qt4.editor import Editor

from .binder import Binder
from .binding import Binding
from .qt import QtGui
from .raw_widgets import ButtonGroup


class TraitsUI(Binder):
    """ Place a Traits UI `Item` into a `Bound` layout.

    The automatically-added traits are only those for `QWidget`, not whatever
    widget the root control of the `Item` may turn out to be. This
    :class:`~.Binder` can only be used in the context of a :class:`~.Bound`
    layout because it needs to be specially recognized and initialized.
    """
    qclass = QtGui.QWidget

    #: The Traits UI Item to display. Any label is ignored.
    item = Instance(Item)

    # The `UI` object of the whole `View`.
    _ui = Any()

    # The initialized editor.
    _editor = Any()

    def __init__(self, item=None, **traits):
        super(TraitsUI, self).__init__(item=item, **traits)

    def initialize_item(self, ui):
        """ Initialize the item using the Traits UI `UI` object.
        """
        item = self.item
        name = item.name
        object = eval(item.object_, globals(), ui.context)
        trait = object.base_trait(name)

        # Get the editor factory associated with the Item:
        editor_factory = item.editor
        if editor_factory is None:
            editor_factory = trait.get_editor().trait_set(**item.editor_args)

            # If still no editor factory found, use a default text editor:
            if editor_factory is None:
                from traitsui.qt4.text_editor import ToolkitEditorFactory
                editor_factory = ToolkitEditorFactory()

            # If the item has formatting traits set them in the editor
            # factory:
            if item.format_func is not None:
                editor_factory.format_func = item.format_func

            if item.format_str != '':
                editor_factory.format_str = item.format_str

            # If the item has an invalid state extended trait name, set it
            # in the editor factory:
            if item.invalid != '':
                editor_factory.invalid = item.invalid

        # Create the requested type of editor from the editor factory:
        factory_method = getattr(editor_factory, item.style + '_editor')
        editor = factory_method(ui, object, name, item.tooltip, None)
        editor.trait_set(
            item=item,
            object_name=item.object,
        )
        self._editor = editor
        self._ui = ui

    def construct(self):
        item = self.item
        editor = self._editor
        ui = self._ui
        # Tell the editor to actually build the editing widget.  Note that
        # "inner" is a layout.  This shouldn't matter as individual editors
        # shouldn't be using it as a parent anyway.  The important thing is
        # that it is not None (otherwise the main TraitsUI code can change
        # the "kind" of the created UI object).
        inner = QtGui.QVBoxLayout()
        editor.prepare(inner)
        control = editor.control

        if item.style_sheet:
            control.setStyleSheet(item.style_sheet)

        # Set the initial 'enabled' state of the editor from the factory:
        editor.enabled = editor.factory.enabled

        # Give the editor focus if it requested it:
        if item.has_focus:
            control.setFocus()

        # We ignore the geometry options of the Item. At least for now.

        # Bind the editor into the UIInfo object name space so it can be
        # referred to by a Handler while the user interface is active:
        id = item.id or item.name
        ui.info.bind(id, editor, item.id)

        ui._scrollable |= editor.scrollable

        # Also, add the editors to the list of editors used to construct
        # the user interface:
        ui._editors.append(editor)

        # If the editor is conditionally visible, add the visibility
        # 'expression' and the editor to the UI object's list of monitored
        # objects:
        if item.visible_when != '':
            ui.add_visible(item.visible_when, editor)

        # If the editor is conditionally enabled, add the enabling
        # 'expression' and the editor to the UI object's list of monitored
        # objects:
        if item.enabled_when != '':
            ui.add_enabled(item.enabled_when, editor)

        self.qobj = control


class QtBoundEditor(Editor):
    """ Qt implementation of the ``BoundEditor``.
    """

    #: The ``Binder`` object being displayed.
    binder = Instance(Binder)

    def __init__(self, parent, **traits):
        """ Initializes the editor object.
        """
        HasPrivateTraits.__init__(self, **traits)
        self.old_value = Undefined

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        binder = self.factory.binder
        for child in binder:
            if isinstance(child, TraitsUI):
                child.initialize_item(self.ui)
        binder.construct()
        binder.configure()
        self.binder = binder
        context = self._get_context()
        for button_group in self.factory.button_groups.values():
            button_group.construct()
            button_group.configure()
            button_group.add_buttons_from_context(context)
        for binding in self.factory.bindings:
            binding.bind(binder, context)
        if self.factory.configure is not None:
            self.factory.configure(binder, context)
        if isinstance(binder.qobj, QtGui.QLayout):
            self.control = QtGui.QWidget()
            self.control.setLayout(binder.qobj)
        else:
            self.control = binder.qobj
        if self.factory.stylesheet is not None:
            self.control.setStyleSheet(self.factory.stylesheet)

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        if self.ui is None:
            return

        for binding in self.factory.bindings:
            binding.unbind()

        self.binder.dispose()
        self.binder = None

        # Break linkages to references we no longer need:
        self.object = self.ui = self.item = self.factory = self.control = \
            self.label_control = self.old_value = self._context_object = None

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
        editor.

        No-op in our case.
        """
        pass

    def _get_context(self):
        """ Return a context for evaluating binding expressions.
        """
        context = self.ui.context.copy()
        context.update(self.factory.button_groups)
        context.update(self.factory.extra_context)
        # Add any binders with IDs to the context.
        for child in self.binder:
            if child.id:
                context[child.id] = child
        return context


class BoundEditor(EditorFactory):
    """ Editor for Binder-wrapped Qt widgets.
    """

    #: The Binder instance.
    binder = Instance(Binder)

    #: The list of ``Bindings``.
    bindings = List(Instance(Binding))

    #: Any extra data to put into the context.
    extra_context = Dict()

    #: A function to call to configure the Binder. It takes two arguments, the
    #: root Binder and the dictionary that is used as the context for
    #: evaluating the bindings.
    configure = Callable()

    #: The Qt stylesheet to apply to the root control.
    stylesheet = Either(Str, None)

    #: Mapping of names to `ButtonGroups`.
    button_groups = Dict(Str, Instance(ButtonGroup))

    def _get_simple_editor_class(self):
        return QtBoundEditor

    def _get_custom_editor_class(self):
        return QtBoundEditor

    def _get_text_editor_class(self):
        return QtBoundEditor

    def _get_readonly_editor_class(self):
        return QtBoundEditor


class Bound(Item):
    """ Convenience ``Item`` for placing a ``Binder`` in a ``View``.
    """

    def __init__(self, binder, *bindings, **kwds):
        extra_context = kwds.pop('extra_context', {})
        if 'label' not in kwds:
            kwds.setdefault('show_label', False)
        configure = kwds.pop('configure', None)
        stylesheet = kwds.pop('stylesheet', None)
        button_groups = kwds.pop('button_groups', {})
        # FIXME: find a better workaround for using `trait_modified`.
        # We use it because Traits UI expects *a* trait here. This is one that
        # is unlikely to appear elsewhere in Traits UIs. Fortunately, it is one
        # that every `HasTraits` class already has, and it is an `Event`, which
        # prevents Traits UI from trying to get its value.
        parsed_bindings = list(map(Binding.parse, bindings))
        super(Bound, self).__init__(
            value='trait_modified',
            editor=BoundEditor(
                binder=binder,
                bindings=parsed_bindings,
                extra_context=extra_context,
                configure=configure,
                stylesheet=stylesheet,
                button_groups=button_groups,
            ),
            **kwds)

    def __repr__(self):
        lines = [
            '{0.__name__}('.format(type(self)),
            '    {0!r},'.format(self.editor.binder),
        ]
        for binding in self.editor.bindings:
            if type(binding).__str__ is not object.__str__:
                lines.append("    '{0}',".format(binding))
            else:
                lines.append('    {0!r},'.format(binding))
        if self.editor.configure:
            lines.append('    configure={0.configure!r},'.format(self.editor))
        if self.editor.extra_context:
            lines.append('    extra_context={0.extra_context!r},'.format(
                self.editor))
        if self.editor.button_groups:
            lines.append('    button_groups={0.button_groups!r},'.format(
                self.editor))
        if self.show_label:
            lines.append('    label={0.label!r},'.format(self))
        lines.append(')')
        return '\n'.join(lines)
