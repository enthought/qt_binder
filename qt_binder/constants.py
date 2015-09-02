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

# Some enums internal to ctraits.
FORCE_INSTANCE_TRAIT = 2
EXISTING_INSTANCE_TRAIT = 1
EXISTING_TRAIT = 0
FORCE_CLASS_TRAIT = -1
BASE_TRAIT = -2
EXISTING_NOTIFIERS = 0
FORCE_NOTIFIERS = 1

# Some names that are used to store things in the __dict__s of Binders.
DELAYED_CONNECTION = '<__DelayedConnection__>'
DELAYED_SETATTR = '<__DelayedSetattr__>'
