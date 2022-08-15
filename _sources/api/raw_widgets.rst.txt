:mod:`qt_binder.raw_widgets`
============================

Mostly automated wrappers around all of the `QWidgets` and `QLayouts` provided
in :mod:`PySide.QtGui`. Generally, the |Binder| is named by dropping the
leading `Q`. Only a few of these are minimally customized when it is necessary
to make them useful. Only those are documented here. The `Qt API
reference <http://doc.qt.io/qt-4.8/qtgui-module.html>`_ should be consulted
for details of what properties, signals, and slots are defined.

.. currentmodule:: qt_binder.raw_widgets

----

.. data:: binder_registry

    The global |TypeRegistry| mapping PySide/PyQt types to their default |Binder|
    class.

----

.. autoclass:: ComboBox
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: Layout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: BoxLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: VBoxLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: HBoxLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: StackedLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: FormLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: WithLayout
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: Splitter
    :members:
    :undoc-members:
    :show-inheritance:

----

.. autoclass:: ButtonGroup
    :members:
    :undoc-members:
    :show-inheritance:

.. # substitutions

.. |Binder| replace:: :class:`~.Binder`
.. |TypeRegistry| replace:: :class:`~.TypeRegistry`
