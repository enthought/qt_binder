QtBinder
========

QtBinder thinly wraps Qt widgets with Traits.

The main goal of QtBinder is to provide a way to build Qt UIs with Traits
models with an emphasis on transparency and flexibility. The core is the
`Binder` class that automatically wraps a `QObject` and exposes its properties,
signals, and slots as traits. Subclasses of a particular `Binder` can add
traits and methods to customize the widget and expose useful patterns of
communication between UI and model over the raw Qt API.

`Binder` widgets can be used inside a Traits UI `View` using a special `Item`
called `Bound`. `Binder` widgets can be bound to model traits using binding
expressions.

Getting Started
---------------

The documentation took me quite some time. Please take a look. The examples
aren't much to look at right now, but give a flavor of what is going to be
possible.

How Can I Help?
---------------

I'm glad you asked! Please take a look at what's here and see if it might solve
some of your Traits UI pains. Transitioning off of Traits UI completely is
a longer-term goal (see the docs), so just focus on the parts that are
particularly painful.
