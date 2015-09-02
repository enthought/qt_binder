Welcome to QtBinder!
====================

QtBinder thinly wraps Qt widgets with Traits.

The main goal of QtBinder is to provide a way to build Qt UIs with Traits
models with an emphasis on transparency and flexibility. The core is the
|Binder| class that automatically wraps a `QObject` and exposes its properties,
signals, and slots as traits. Subclasses of a particular |Binder| can add
traits and methods to customize the widget and expose useful patterns of
communication between UI and model over the raw Qt API.

|Binder| widgets can be used inside a Traits UI `View` using a special `Item`
called |Bound|. |Binder| widgets can be bound to model traits using
:ref:`binding expressions<traits_ui>`.

.. _why_qt_binder:

When do I use QtBinder over Traits UI?
--------------------------------------

The two major pain points of Traits UI are getting widgets laid out precisely
the way you need them to and customizing the behavior of editors in ways not
intended by the original author. QtBinder addresses the layout problem by
providing access to all of the layout tools that raw Qt has. It is even
possible to lay out widgets in Qt Designer and attach the appropriate |Binder|
to each widget.

|Bound| can be used to replace one normal `Item` in a Traits UI `View`, or by
using a hierarchical layout |Binder|, it can replace some or all of what you
would otherwise use normal Traits UI `Groups` for layout. You can use as much
or as little of QtBinder as you need. It is easy to spot-fix the behavior of
just one editor by replacing it with a `Binder` and leave the rest of the
`View` alone. You do not have to wait until QtBinder has replicated the
functionality of all Traits UI editors before using it to solve smaller
problems.


Contents
--------

.. toctree::
   :maxdepth: 2

   principles
   traits_ui
   todo
   api/index



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. # substitutions

.. |Binder| replace:: :class:`~.Binder`
.. |Bound| replace:: :class:`~.Bound`
