.. _traits_ui:

Traits UI Integration
=====================

The |Bound| class is a Traits UI `Item` that can be used to place a |Binder|
widget into a Traits UI `View` and bind it to traits on the model or `Handler`.
It comes with its own `Editor` that knows how to set up the |Binder| and use it
as the control for the `Item`.

The |Bound| constructor takes a |Binder| instance and some bindings. Bindings
are either instances of |Binding| subclasses or, more conveniently,
specially-formatted strings that will be parsed to |Binding| subclass
instances.

::

    traits_view = View(
        Bound(
            HBoxLayout(
                Label(id='label'),
                LineEdit(id='edit', placeholderText=u'An integer'),
            ),
            Factory('edit.validator', QtGui.QIntValidator),
            'label.text << handler.label',
            'edit.text := object.text',
            'spacing = 5',
        ),
    )

This example `View` succinctly demonstrates most of the Traits UI features. The
`HBoxLayout` is a |Binder| that transparently wraps the `QHBoxLayout` Qt layout
object. It is slightly customized with a constructor that lets you declare the
child widgets by passing |Binder| objects. Thus you can build most typical
layouts using a hierarchy of layout and widget |Binder| objects. |Binder|
constructors can take an `id` keyword argument that sets a name for the
|Binder| that should be unique to the tree of |Binder| objects it is in. This
name will be used to refer to that |Binder| in the bindings that follow. Other
traits that proxy Qt properties can also be set in the |Binder| constructor.
They will be assigned when the underlying `QObject` is assigned to the
|Binder|.

Following the root |Binder| is a list of |Binding| strings or objects. These
follow a pattern of `'binder_trait <operator> model_trait_or_expression'`. On
the left of the operator is either the name of a trait on the root |Binder|
(e.g. `spacing` refers to the `HBoxLayout.spacing` property) or a dotted
reference to a trait on a descendant |Binder| that has provided an explicit
`id` (e.g. `edit.text` refers to the `LineEdit.text` property).

On the right side of the operator is an expression evaluated in the Traits UI
context. For a |Binding| that writes back to the model (`:=`/|SyncedWith| and
`>>`/|PushedTo|), this is restricted to a simple extended trait reference; i.e.
`object.foo.bar` but not `object.foo.bar + 10`. This context starts with the
Traits UI context (i.e. has `object` and `handler` at a minimum) and is
extended with any |Binder| in the tree with a non-empty `id`. For
`<<`/|PulledFrom|, the expression will be parsed for extended trait references
and the binding will be evaluated whenever it changes.
For example, `format(handler.template, object.child.value)` will re-evaluate and
assign to the left-hand side whenever `handler.template` OR
`object.child.value` changes.

.. note:: Annoyingly, at the moment we cannot detect when such a dotted
    reference has a non-terminal non-`HasTraits` object. In the example above,
    `handler.template.format(object.child.value)` would cause an error because
    `handler.template` is a string, not a `HasTraits` object to which
    a listener can be attached.

There are four operators that can be used in the string representations of
|Binding| objects:

* `=` or |SetOnceTo|: Set a value once. This evaluates the right-hand side once
  when the binding is established. No notifications will be sent afterwards.

* `<<` or |PulledFrom|: Pull values from the model. This evaluates the
  right-hand side once when the binding is established and whenever any traits
  used in the expression fire a change notification.

* `>>` or |PushedTo|: Push values from the |Binder| to the model. When the
  |Binder| trait on the left-hand side changes, this will assign the new value
  to the attribute referenced on the right-hand side. No value is assigned on
  initialization.

* `:=` or |SyncedWith|: A combination of |PulledFrom| and |PushedTo| to
  synchronize a binder trait with a model trait. Because the right-hand side of
  |PushedTo| is restricted to plain attribute references, so is this. Like
  |PulledFrom|, the right-hand side will be evaluated when the binding is
  established and assigned to the left-hand side to initialize it.

And the last |Binding| cannot be put into string form:

* |Factory|: Call the provided function once when the binding is established,
  and set the value. No notifications will be sent afterwards.

Bindings which initialize a value (i.e. |SetOnceTo|/`=`, |PulledFrom|/`<<`,
|SyncedWith|/`:=`, and |Factory|) will be evaluated in the order in which they
are specified. This can be important for initializing some Qt objects. For
example, setting up validator properties before assigning the value.

|Bound| takes the following optional keyword arguments:

    label : `unicode`
        Like the normal `Item` `label` argument, except that if one is not
        provided, then |Bound| will set `show_label=False`. Since the |Bound|
        `Item` is not exclusively associated with any single trait like other Traits UI
        `Items` are, the default Traits UI behavior of using the trait name as
        a label is not useful.

    extra_context : `dict`
        Any extra objects that should be added to the context used to evaluate the
        right-hand-side of bindings.

    configure : function with signature `configure(binder, context)`
        A function to call after the root |Binder| has been constructed and the
        bindings established but before display. It will be passed the root
        |Binder| and the context dictionary. This can be used to do customizations
        using the raw Qt API that may not be achievable using bindings alone.

    stylesheet : `unicode`
        A `Qt stylesheet <http://doc.qt.io/qt-4.8/stylesheet.html>`_
        applied to the root control.

    button_groups : `dict` naming |ButtonGroup| objects
        Collect buttons in the UI into named, bindable groups that will be
        added to the context.

.. # substitutions

.. |Binder| replace:: :class:`~.Binder`
.. |Bound| replace:: :class:`~.Bound`
.. |Binding| replace:: :class:`~.Binding`
.. |SetOnceTo| replace:: :class:`~.SetOnceTo`
.. |Factory| replace:: :class:`~.Factory`
.. |PulledFrom| replace:: :class:`~.PulledFrom`
.. |PushedTo| replace:: :class:`~.PushedTo`
.. |SyncedWith| replace:: :class:`~.SyncedWith`
.. |ButtonGroup| replace:: :class:`~.ButtonGroup`

