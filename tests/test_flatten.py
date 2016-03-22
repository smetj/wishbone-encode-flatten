#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import pytest

from wishbone.event import Event, Metric
from wishbone_encode_flatten import Flatten
from wishbone.actor import ActorConfig
from utils import getter


def test_module_Flatten_default():

    '''Tests the default behavior.'''

    actor_config = ActorConfig('flatten', 100, 1, {}, "")
    flatten = Flatten(actor_config)

    flatten.pool.queue.inbox.disableFallThrough()
    flatten.pool.queue.outbox.disableFallThrough()
    flatten.start()

    e = Event({"server": {"host01": {"memory": {"free": 10, "consumed": 90}}}})

    flatten.pool.queue.inbox.put(e)
    one = getter(flatten.pool.queue.outbox)
    two = getter(flatten.pool.queue.outbox)

    assert isinstance(one.get(), Metric)
    assert isinstance(two.get(), Metric)

    assert one.get().name == 'server.host01.memory.free'
    assert two.get().name == 'server.host01.memory.consumed'
