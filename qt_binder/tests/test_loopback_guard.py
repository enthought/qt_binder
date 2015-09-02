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

import unittest

import six

from traits.api import HasTraits, Instance, List, on_trait_change

from ..loopback_guard import LoopbackGuard, LoopbackContext


class TestLoopbackGuard(unittest.TestCase):
    """
    Unit tests that exercise the LoopbackGuard class directly.

    """
    def test_acquire_release_balanced(self):
        # Check that we can acquire and release the loopback guard
        # multiple times.

        to_add = {'item 0': 3, 'item 1': 4, 'item 2': 2}
        guard = LoopbackGuard()

        # Acquire the guard for the items in to_add.
        for obj, times in to_add.items():
            for _ in range(times):
                guard.acquire([obj])

        self.assertDictEqual(guard.locked_items, to_add)

        # Release the guard.
        for obj, times in to_add.items():
            for _ in range(times):
                guard.release([obj])

        self.assertIsNone(guard.locked_items)


class TestLoopbackContext(unittest.TestCase):
    """
    Unit tests that exercise the LoopbackGuard class through
    the LoopbackContext context manager.

    """

    def _check_loopback_context_manager(self, cm, guard, items):
        # Check that we can add items to a loopback context manager, and that
        # the items are properly released when the context is exited.

        with cm:
            six.assertCountEqual(self, guard.locked_items, items)
            for item in items:
                self.assertIn(item, guard)

        self.assertIsNone(guard.locked_items)
        for item in items:
            self.assertNotIn(item, guard)

    def test_loopback_context_direct(self):
        # Instantiate a context manager directly.
        items = ['a', 'b', 'c']
        guard = LoopbackGuard()
        cm = LoopbackContext(guard, items)
        self._check_loopback_context_manager(cm, guard, items)

    def test_loopback_context_call(self):
        # Instantiate a context manager by calling the loopback guard with the
        # items to be locked.
        items = ['a', 'b', 'c']
        guard = LoopbackGuard()
        cm = guard(*items)
        self._check_loopback_context_manager(cm, guard, items)


class Dummy(object):
    pass


class E(HasTraits):

    a = Instance(Dummy, ())

    b = Instance(Dummy, ())

    # List of traits that have updated.
    updates = List

    # Loopback guard to protect `a` from cyclic updates.
    guard = Instance(LoopbackGuard, ())

    @on_trait_change('a')
    def _a_updated(self, new):
        with self.guard(self.a):
            self.updates.append('b')
            self.b = new

    @on_trait_change('b')
    def _b_updated(self, new):
        if self.a not in self.guard:
            self.updates.append('a')
            self.a = new


class TestLoopbackGuardUseCase(unittest.TestCase):
    """
    Test suite for the common LoopbackGuard use case.

    """
    def test_loopback_prevents_cyclic_updates(self):
        # Check that the loopback guard prevents cyclic updates in `a`.
        e = E()
        e.a = Dummy()
        self.assertEqual(e.updates, ['b'])

    def test_normal_cyclic_updates(self):
        # Test that the loopback guard does not stand in the way of the
        # normal traits behavior when `b` is updated.
        e = E()
        e.b = Dummy()  # The loopback guard does not protect `b`.
        self.assertEqual(e.updates, ['a', 'b'])
