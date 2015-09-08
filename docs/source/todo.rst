To Do
=====

Short Term
----------

* Demonstrate some fancier use cases that Traits UI does not handle well, like
  double-ended sliders made in Chaco (with histogram of a dataset being shown
  underneath).

* Bikeshed all the names.

Long Term
---------

* Develop a reasonable story for the reverse wrapping: wrapping Traits object
  in the `Qt item models API <http://doc.qt.io/qt-4.8/model-view-programming.html>`_.
  Traits UI's `TabularAdapter` is a reasonable start, but it misses a lot of
  opportunities to be ideal according to our :ref:`Core Principles <core_principles>`.

* Have sufficient replacements for all common Traits UI editors and the ways
  that we have hacked them. The following are those that are sufficiently
  complicated that a configured raw widget |Binder| would not suffice (or are
  not otherwise covered elsewhere here).

  - `TextEditor`: we still need a `LineEdit` customization that converts
    specific Python objects (floats, ints, whatevers) to/from strings and
    validates the same.
  - `EnumEditor`: there are two distinct use cases, to select from a list of
    specific items or to allow write-in values with some recommended choices.
    Keep those use cases separate.
  - `BoundsEditor`: don't reuse the implementation. Use `(low, high)` tuples
    for both the value and the outer range. It's easier to handle the events
    that way. Also, we want to be able to grab the middle of the slider to move
    the whole range and not just each end independently. Keep it
    interface-compatible with the Chaco double-ended slider.
  - `ColorEditor`: design a nicer UI than the current one.
  - `DateEditor`
  - `TimeEditor`
  - `DirectoryEditor`
  - `FileEditor`
  - `SetEditor`

  As you can see, it's not that much.

* Inspect a |Binder| hierarchy and write it out as a Qt Designer `.ui` file so
  you can prototype the |Binder| using the simple declarative syntax, then
  tweak it quickly to look excellent for production.

* Wrap `QtQuick components <http://doc.qt.io/qt-4.8/qtquick.html>`_.
  QML is going to be particularly good for heavily customized table widgets.

Un-goals
--------

* Other toolkits.

* Constraint-based layout. It can be useful for some advanced use cases, but is
  largely unnecessary for almost all of our use cases. It can be hard to debug
  without the right tooling (a la Apple), and the simple use cases sometimes
  fail inscrutably. Of course, it can be added independently as a `QLayout` if
  needed.

.. # substitutions

.. |Binder| replace:: :class:`~.Binder`
.. |Bound| replace:: :class:`~.Bound`

