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

from collections import Counter, deque
import keyword
import weakref

import six

from traits.api import HasStrictTraits, Instance, List, Property, Str, \
    TraitType, Undefined

from .constants import DELAYED_CONNECTION, DELAYED_SETATTR, \
    EXISTING_INSTANCE_TRAIT, EXISTING_NOTIFIERS, FORCE_INSTANCE_TRAIT, \
    FORCE_NOTIFIERS
from .loopback_guard import LoopbackGuard
from .qt import QtCore


NULL_VARIANT_VALUES = {
    'QString': u'',
}


def _to_str(t):
    if isinstance(t, QtCore.QByteArray):
        try:
            # PyQt4
            t = bytes(t).decode()
        except TypeError:
            # PySide
            t = str(t)
    else:
        t = str(t)
    return t


def _slot_name(name):
    return '_{}_property_changed'.format(name)


def _slot_for(ref, name):
    def slot(*args):
        obj = ref()
        if obj is not None:
            if len(args) == 1:
                args = args[0]
            obj.trait_property_changed(name, Undefined, args)
    slot.__name__ = _slot_name(name)
    return slot


def _guard_against_null_variant(value):
    """ Convert PyQt4's QPyNullVariant to a reasonable value.
    """
    if type(value).__name__ == 'QPyNullVariant':
        return NULL_VARIANT_VALUES.get(value.typeName(), None)
    return value


def _python_name_for_qt_name(qname):
    """ Convert forbidden Qt names to valid Python names, following PySide/PyQt
    rules.

    E.g. 'raise' -> 'raise_'
    """
    if keyword.iskeyword(qname):
        qname += '_'
    return qname


class QtTrait(TraitType):
    """ Base class for Qt proxy traits on :class:`~.Binder` classes.

    Each subclass should override :meth:`get` and :meth:`set`. All
    :class:`~.QtTrait` subclasses are property-like traits.

    If there is a Qt ``Signal`` that should be connected to to propagate
    notifications, assign it to the ``signal`` attribute. The Qt ``Signal``
    will only be connected to when a Traits listener is attached to this trait.
    """

    def __init__(self, *args, **metadata):
        self.signal = None
        super(QtTrait, self).__init__(transient=True, **metadata)

    def get(self, object, name):
        """ Get the value of this trait.
        """
        raise NotImplementedError

    def set(self, object, name, value):
        """ Set the value of this trait and notify listeners.
        """
        raise NotImplementedError

    def connect_signal(self, object, name):
        """ Connect to the Qt signal, if any.
        """
        if self.signal is None:
            # No signal to connect to.
            return
        qobj = object.qobj
        slot = _slot_for(weakref.ref(object), name)
        object.__dict__[slot.__name__] = slot
        # Use the classmethod form for PyQt4 compatibility.
        QtCore.QObject.connect(qobj, self.signal, slot)

    def disconnect_signal(self, object, name):
        """ Disconnect from the Qt signal, if any.
        """
        if self.signal is None:
            # No signal to disconnect from.
            return
        slot_name = _slot_name(name)
        slot = object.__dict__.pop(slot_name, None)
        if slot is not None:
            # Use the classmethod form for PyQt4 compatibility.
            QtCore.QObject.disconnect(object.qobj, self.signal, slot)


class QtProperty(QtTrait):
    """ Proxy trait for a Qt static property.

    Pass in a ``QMetaProperty`` from the ``QMetaObject``.
    """
    def __init__(self, meta_prop, **metadata):
        super(QtProperty, self).__init__(**metadata)
        self.meta_prop = meta_prop
        if meta_prop.hasNotifySignal():
            self.signal = QtCore.SIGNAL(meta_prop.notifySignal().signature())

    def get(self, object, name):
        """ Get the value of this trait.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            if name in d:
                return d[name]
            else:
                msg = ("Property {0!r} not available until Binder is given "
                       "its QObject.".format(name))
                raise AttributeError(msg)
        try:
            value = self.meta_prop.read(qobj)
        except RuntimeError:
            # PySide has a bug such that it will not return flags sometimes,
            # like for QGroupBox.alignment.
            name = self.meta_prop.name()
            if hasattr(qobj, name):
                value = getattr(qobj, name)()
            else:
                # Nothing else we can do.
                raise
        # PyQt4 will sometimes return a QPyNullVariant via this API even if it
        # converts it to the correct null value for the type for the property
        # attribute on the QObject itself.
        value = _guard_against_null_variant(value)
        return value

    def set(self, object, name, value):
        """ Set the value of this trait and notify listeners.

        If there is a Qt ``Signal`` for this property, it will notify the
        listeners. If there is not one for this property, this method will
        explicitly send a notification.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            d[name] = value
            return
        try:
            old = self.meta_prop.read(qobj)
        except RuntimeError:
            # PySide has a bug such that it will not return flags sometimes,
            # like for QGroupBox.alignment.
            name = self.meta_prop.name()
            if hasattr(qobj, name):
                old = getattr(qobj, name)()
                setter = getattr(qobj, 'set' + name.title())
                setter(value)
            else:
                # Nothing else we can do.
                raise
        else:
            # Happy path.
            self.meta_prop.write(qobj, value)
        if self.signal is None:
            # Propagate the event notification ourselves.
            object.trait_property_changed(name, old, value)


class QtDynamicProperty(QtTrait):
    """ A Qt dynamic property added to the ``QObject``.

    The dynamic property will be created on the ``QObject`` when it is
    added to the :class:`~.Binder`. The default value given to this trait will
    be the initial value. It should be an object that can be passed to
    ``QVariant``.

    Because most dynamic properties will be added this way to support Qt
    stylesheets, by default when the property is assigned a new value, the
    ``QObject`` associated with the ``Binder`` (which should be a ``QWidget``)
    will be made to redraw itself in order to reevaluate the stylesheet rules
    with the new value. Turn this off by passing ``styled=False`` to the
    constructor.
    """

    def __init__(self, default_value=None, **metadata):
        metadata['is_dynamic_property'] = True
        metadata.setdefault('styled', True)
        super(QtDynamicProperty, self).__init__(
            default_value=default_value, **metadata)

    def get(self, object, name):
        """ Get the value of this trait.
        """
        qobj = object.qobj
        if qobj is None:
            delayed_attrs = object.__dict__.get(DELAYED_SETATTR, {})
            return delayed_attrs.get(name, self.default_value)
        return qobj.property(name)

    def set(self, object, name, value):
        """ Set the value of this trait and notify listeners.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            d[name] = value
            return
        old = qobj.property(name)
        qobj.setProperty(name, value)
        if self.metadata.get('styled', True) and hasattr(qobj, 'style'):
            style = qobj.style()
            style.unpolish(qobj)
            style.polish(qobj)
        object.trait_property_changed(name, old, value)


class QtGetterSetter(QtTrait):
    """ Proxy for a getter/setter pair of methods.

    This is used for ``value()/setValue()`` pairs of methods that are
    frequently found in Qt, but which are not bona fide Qt properties.

    If the names follow this convention, you only need to pass the name of the
    getter method. Otherwise, pass both.
    """
    def __init__(self, getter_name, setter_name=None, **metadata):
        super(QtGetterSetter, self).__init__(**metadata)
        self.getter_name = getter_name
        if setter_name is None:
            setter_name = 'set' + getter_name.title()
        self.setter_name = setter_name

    def get(self, object, name):
        """ Get the value of this trait.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            if name in d:
                return d[name]
            else:
                msg = ("Getter {0!r} not available until Binder is given "
                       "its QObject.".format(name))
                raise AttributeError(msg)
        return getattr(qobj, _python_name_for_qt_name(self.getter_name))()

    def set(self, object, name, value):
        """ Set the value of this trait and notify listeners.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            d[name] = value
            return
        old = self.get(object, name)
        getattr(qobj, _python_name_for_qt_name(self.setter_name))(value)
        object.trait_property_changed(name, old, value)


class QtSlot(QtTrait):
    """ Proxy for a Qt slot method.

    In general use, this trait will only be assigned to. If the slot takes no
    arguments, the value assigned is ignored. If the slot takes one argument,
    the value assigned is passed to the slot. If the slot takes more than one
    argument, the value assigned should be a tuple of the right size.

    As a convenience, getting the value of this trait will return the slot
    method object itself to allow you to connect to it using the normal Qt
    mechanism.

    The constructor should be passed the ``QMetaMethod`` for this slot.
    """
    def __init__(self, meta_method, **metadata):
        super(QtSlot, self).__init__(**metadata)
        self.meta_method = meta_method
        self.qname = meta_method.signature().split('(')[0]
        self.n_args = len(meta_method.parameterTypes())

    def get(self, object, name):
        """ Get the underlying method object.
        """
        return getattr(object.qobj, _python_name_for_qt_name(self.qname))

    def set(self, object, name, value):
        """ Set the value of this trait.

        See :class:`~.QtSlot` for details on how the value is processed.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            d[name] = value
            return
        args = self._process_args(value)
        getattr(qobj, _python_name_for_qt_name(self.qname))(*args)

    def _process_args(self, value):
        if self.n_args == 0:
            # The value is ignored. Setting any value counts as just calling
            # the empty slot.
            args = ()
        elif self.n_args == 1:
            args = (value,)
        else:
            args = value
        return args


class QtSignal(QtSlot):
    """ Proxy for a Qt signal method.

    In general use, this trait will only be listened to for events that are
    emitted internally from Qt. However, it can be assigned values, with the
    same argument semantics as :class:`~.QtSlot`. Like :class:`~.QtSlot`,
    getting the value of this trait will return the signal method object itself
    for you to connect to it using the normal Qt mechanism.

    The constructor should be passed the ``QMetaMethod`` for this signal.
    """
    def __init__(self, meta_method, **metadata):
        super(QtSignal, self).__init__(meta_method, **metadata)
        self.signal = QtCore.SIGNAL(meta_method.signature())

    def set(self, object, name, value):
        """ Emit the signal with the given value.

        See :class:`~.QtSlot` for details on how the value is processed.
        """
        qobj = object.qobj
        if qobj is None:
            d = object.__dict__.setdefault(DELAYED_SETATTR, {})
            d[name] = value
            return
        args = self._process_args(value)
        if len(args) == 0:
            # Use the QMetaMethod to invoke the signal for PyQt4 compatibility.
            self.meta_method.invoke(qobj)
        else:
            # In both PyQt4 and PySide, QMetaMethod.invoke() does not
            # automatically convert the arguments, so emit it directly.
            getattr(qobj, name).emit(*args)


class Rename(object):
    """ Specify that an automatic QtTrait be renamed.

    Use at the class level of a :class:`~.Binder` to rename the trait to
    something else.

    For :class:`~.QtSlot` traits with multiple signatures, only the primary
    part of the name (without the mangled type signature) needs to be given.

    Since one cannot use both a :class:`~.Default` and :class:`~.Rename` at the
    same time, one can also specify the default value here.
    """

    def __init__(self, qt_name, default=Undefined):
        """ Rename an automatic QtTrait.

        Parameters
        ----------
        qt_name : str
            The name of the Qt property/signal/slot being renamed.
        default : object, optional
            The default value, if any.
        """
        self.qt_name = qt_name
        self.default = default

    def __repr__(self):
        extra = ''
        if self.default is not Undefined:
            extra = ', {0.default!r}'.format(self)
        return '{0.__name__}({1.qt_name!r}{2})'.format(type(self), self, extra)


class Default(object):
    """ Specify a default value for an automatic QtTrait.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '{0.__name__}({1.value!r})'.format(type(self), self)


class Binder(HasStrictTraits):
    """ Traited proxy for a ``QObject`` class.

    The default proxy traits will be automatically assigned by inspecting the
    Qt class specified in the :attr:`qclass` class attribute. Since this
    inspection process can be time consuming, compared to normal class
    construction, this will only be done the first time the ``Binder`` class is
    instantiated.

    For those traits that proxy a Qt ``Signal`` (or property that has
    a ``Signal``), the Qt signal connection will only be made once a **Traits**
    listener is attached to the proxy trait.

    The :attr:`qobj` can only be assigned once in the ``Binder's`` lifetime.
    """

    #: The ``QObject`` **class** that is going to be wrapped by this class.
    qclass = QtCore.QObject

    #: The Qt object instance that is wrapped by the :class:`~.Binder`
    #: instance.
    qobj = Instance(QtCore.QObject)

    #: The loopback guard.
    loopback_guard = Instance(LoopbackGuard, args=())

    #: An ID string, if any. It should be a valid Python identifier.
    id = Str()

    def __init__(self, *args, **traits):
        self._initialize_binder_class()
        # HasStrictTraits.__init__ doesn't take *args.
        super(Binder, self).__init__(**traits)

    def construct(self, *args, **kwds):
        """ Default constructor that will automatically instantiate ``qclass``.
        """
        self.qobj = self.qclass(*args, **kwds)

    def configure(self):
        """ Do any configuration of the ``qobj`` that is needed.
        """
        pass

    def dispose(self):
        """ Remove any connections and otherwise clean up for disposal.

        This does not mark any Qt objects for deletion.
        """
        # Remove all signal connections.
        for name, ctrait in self.traits().items():
            if ctrait.is_trait_type(QtTrait):
                ctrait.trait_type.disconnect_signal(self, name)

    def __iter__(self):
        yield self

    def __repr__(self):
        if self.id:
            args = 'id={0.id!r}'.format(self)
        else:
            args = ''
        return '{0.__name__}({1})'.format(type(self), args)

    #### Private protocol #####################################################

    def _on_trait_change(self, handler, name=None, remove=False,
                         dispatch='same', priority=False, target=None):
        """Causes the object to invoke a handler whenever a trait attribute
        is modified, or removes the association.
        """
        check_this_after = False
        n_notifiers_before = 0
        if isinstance(name, six.string_types) and name != 'anytrait':
            # This was attaching a handler to a single trait.
            force_trait = (FORCE_INSTANCE_TRAIT,
                           EXISTING_INSTANCE_TRAIT)[remove]
            force_notifiers = (FORCE_NOTIFIERS,
                               EXISTING_NOTIFIERS)[remove]
            ctrait = self._trait(name, force_trait)
            if ctrait is not None:
                if ctrait.is_trait_type(QtTrait):
                    check_this_after = True
                    notifiers = ctrait._notifiers(force_notifiers)
                    if notifiers:
                        n_notifiers_before = len(notifiers)
        super(Binder, self)._on_trait_change(
            handler, name=name, remove=remove, dispatch=dispatch,
            priority=priority, target=target)
        if check_this_after:
            notifiers = ctrait._notifiers(force_notifiers)
            if notifiers:
                n_notifiers_after = len(notifiers)
            else:
                n_notifiers_after = 0

            connectors = []
            if not n_notifiers_before and n_notifiers_after:
                connectors.append((ctrait.trait_type.connect_signal, name))
            elif n_notifiers_before and not n_notifiers_after:
                connectors.append((ctrait.trait_type.disconnect_signal, name))

            if self.__dict__.get('qobj', None) is None:
                # No Qt object yet. Delay the connection.
                self.__dict__.setdefault(DELAYED_CONNECTION, deque()).extend(
                    connectors)
            else:
                for func, name in connectors:
                    func(self, name)

    def _initialize_binder_class(self):
        """ Ensure that the binder class has been initialized.
        """
        binder_class = self.__class__
        initialized_name = '_{0.__name__}__binder_class_initialized'.format(
            binder_class)
        # Look directly at the __dict__. Even with the name disambiguation, we
        # still only want to look directly at this class, not its superclasses.
        initialized = binder_class.__dict__.get(initialized_name, False)
        if not initialized:
            renamings = {}
            # Find all requested renamings.
            for name in dir(binder_class):
                obj = getattr(binder_class, name)
                if isinstance(obj, Rename):
                    renamings[obj.qt_name] = name
            qt_class = binder_class.qclass
            meta_object = qt_class.staticMetaObject
            seen = set(binder_class.class_trait_names())
            for i in range(meta_object.propertyCount()):
                meta_prop = meta_object.property(i)
                qname = _python_name_for_qt_name(meta_prop.name())
                name = renamings.get(qname, qname)
                if name not in seen:
                    if name.endswith('_'):
                        # See #21
                        continue
                    binder_class.add_class_trait(name, QtProperty(meta_prop))
                    seen.add(name)

            # Ignore any from the superclass or explicitly defined.
            method_names = []
            method_name_counts = Counter()
            for i in range(meta_object.methodCount()):
                meta_meth = meta_object.method(i)
                qname = _python_name_for_qt_name(
                    meta_meth.signature().split('(')[0])
                name = renamings.get(qname, qname)
                method_names.append(name)
                method_name_counts[name] += 1
            for i in range(meta_object.methodCount()):
                meta_meth = meta_object.method(i)
                qname = _python_name_for_qt_name(
                    meta_meth.signature().split('(')[0])
                name = renamings.get(qname, qname)
                if method_name_counts[name] > 1:
                    # Add the argument types to the name to disambiguate.
                    arg_types = [_to_str(t).rstrip('*')
                                 for t in meta_meth.parameterTypes()]
                    name = '_'.join([name] + arg_types)
                if name not in seen:
                    if name.endswith('_'):
                        # See #21
                        continue
                    method_type = meta_meth.methodType()
                    if method_type == meta_meth.Signal:
                        trait = QtSignal(meta_meth)
                    elif method_type == meta_meth.Slot:
                        trait = QtSlot(meta_meth)
                    else:
                        continue
                    binder_class.add_class_trait(name, trait)
                    seen.add(name)

            # Add all getter/setter pairs that we can identify.
            methods = set()
            for name, class_attr in vars(qt_class).items():
                # sip methoddescriptor objects do not have __call__() defined.
                if (callable(class_attr) or
                        type(class_attr).__name__ == 'methoddescriptor'):
                    methods.add(name)
            methods.difference_update(seen)
            for qname in methods:
                # FIXME: We do not know if these are true getter/setters, where
                # the getter has 0 arguments and the setter has just the 1. For
                # example, `QObject.property(name)` and
                # `QObject.setProperty(name, value)` get misidentified here.
                # Unfortunately, the method objects do not have any information
                # about their argument structure.
                putative_setter = 'set' + qname.title()
                if putative_setter in methods:
                    name = renamings.get(qname, qname)
                    if name.endswith('_'):
                        # See #21
                        continue
                    binder_class.add_class_trait(
                        name, QtGetterSetter(qname, putative_setter))
            setattr(binder_class, initialized_name, True)

    def _qobj_changed(self, old, new):
        """ Hook up any delayed connections to the new ``qobj``.
        """
        assert old is None, ("A Binder should only have one QObject per "
                             "lifetime")
        assert new is not None
        # Hook up any delayed connections causd by Traits listeners that were
        # attached before we had a `qobj`.
        if DELAYED_CONNECTION in self.__dict__:
            delayed_connections = self.__dict__.pop(DELAYED_CONNECTION)
            while delayed_connections:
                func, name = delayed_connections.popleft()
                func(self, name)
        # Create and initialized any Qt dynamic properties that have been
        # requested.
        values = {}
        for name, ctrait in self.traits(is_dynamic_property=True).items():
            values[name] = ctrait.trait_type.get_default_value()[1]
        # And any explicit Defaults.
        cls = type(self)
        for name in dir(cls):
            obj = getattr(cls, name)
            if isinstance(obj, Default):
                values[name] = obj.value
            if isinstance(obj, Rename) and obj.default is not Undefined:
                values[name] = obj.default
        # And any delayed setattrs.
        values.update(self.__dict__.pop(DELAYED_SETATTR, {}))
        self.trait_set(**values)


class Composite(Binder):
    """ Base class for Binders that hold other Binders as children.

    Their ``QObjects`` may or may not have a similar parent-child relationship.
    The ``Composite`` is responsible for constructing its children, configuring
    them, and disposing of them.
    """

    #: The child ``Binder`` instances. This will typically be a Property
    #: returning a list of ``Binders`` that are attributes.
    child_binders = Property(List(Instance(Binder)))

    def configure(self):
        """ Do any configuration of the ``qobj`` that is needed.
        """
        for child in self.child_binders:
            child.configure()
        super(Composite, self).configure()

    def dispose(self):
        """ Remove any connections and otherwise clean up for disposal.

        This does not mark any Qt objects for deletion.
        """
        for child in self.child_binders:
            child.dispose()
        super(Composite, self).dispose()

    def __iter__(self):
        yield self
        for child in self.child_binders:
            for x in child:
                yield x

    def _get_child_binders(self):
        """ Default implementation yielding all of the attributes on this
        object that are ``Binders``.
        """
        children = []
        for name, obj in self.__dict__.items():
            if isinstance(obj, Binder):
                # FIXME: uniquify
                children.append(obj)
        return children


class NChildren(Composite):
    """ Base class for Composite Binders that have arbitrary unnamed children.
    """

    #: Any children. It will be filtered for Binders.
    child_binders = List(Instance(Binder))

    def __repr__(self):
        args = ', '.join(map(repr, self.child_binders))
        if self.id:
            args += ', id={0.id!r}'.format(self)
        return '{0.__name__}({1})'.format(type(self), args)
