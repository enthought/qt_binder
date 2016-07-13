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
""" Dummy objects for `TypeRegistry` testing.
"""

import abc
import six


class A(object):
    pass


class B(A):
    pass


class C(B):
    pass


class D(object):
    pass


class Mixed(A, D):
    pass


@six.add_metaclass(abc.ABCMeta)
class Abstract(object):
    pass


class Concrete(object):
    pass


class ConcreteSubclass(Concrete):
    pass


for typ in (A, B, C, D, Mixed, Abstract, Concrete, ConcreteSubclass):
    typ.__module__ = 'dummies'


Abstract.register(Concrete)
