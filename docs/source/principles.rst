.. _core_principles:

Core Principles
===============

.. _value_added:

#. **Value-added wrapping**: Custom |Binder| classes should only manually wrap
   the Qt API when it adds value. For example, translating Qt enums one-to-one
   to an ad hoc toolkit-neutral form does not add value. |Binder| can
   automatically wrap all Qt properties, signals, and slots. This means that
   a user of the custom subclass can access everything that the Qt widget
   exposes even if the author did not think to expose it. Value-added wrapping
   encapsulates patterns of communication and coordinates multiple moving
   pieces internal to the widget to expose a bindable Traits API.

#. **Thin, transparent wrapping**: This is a library for *using* Qt to build
   UIs, not hide it behind a toolkit-neutral abstraction.

#. **Small core**: The core should remain tiny so that it can be understood and
   traced through by users of QtBinder who are debugging their code.

#. **Graded transition from Traits UI**: |Bound| is a straightforward
   Traits UI `Item` that can be used wherever any other `Item` could be used in
   Traits UI. It can be used in a very focused manner to fix one or two places
   where the extra flexibility of QtBinder is necessary and ignored elsewhere.
   It can also be used to provide the whole `View` when desired. Use of
   QtBinder should not be held up because we have not added enough value-added
   widgets yet.

#. **Bind to existing instances**: All |Binder| classes can either instantiate
   their underlying `QWidget` or be provided an existing one. This allows us to
   lay out an entire UI in Qt Designer, instantiate it from the `.ui` file,
   then attach the desired |Binder| to individual widgets inside of it.

#. **Do one thing well**: Custom |Binder| subclasses should attempt to
   encapsulate one particular pattern of using their wrapped widget. It should
   not try to switch between different patterns based on configuration (unless
   if the intended pattern requires that the widget switch behaviors live). The
   logic needed to synchronize the widget state with the model state can
   sometimes get hairy. Dealing with multiple patterns conditionally
   complicates this part of the code, which makes it harder to customize for
   new purposes.

#. **Pay for what you use**: |Binder| wraps all Qt signals, but it will only
   connect to them and incur the cost of converting the signal values to Python
   objects when a Traits listener is attached to the signal trait.

.. # substitutions

.. |Binder| replace:: :class:`~.Binder`
.. |Bound| replace:: :class:`~.Bound`
