#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       flatten.py
#
#       Copyright 2015 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
from wishbone.event import Event, Metric
from gevent import monkey
monkey.patch_time()
from time import time


class Flatten(Actor):

    '''**Flattens a dict structure of arbitrary depth into individual metric events.**

        This module takes a <dict> structure and recursively travels it
        flattening the namespace into a dotted format untill a numeric value
        is encountered. For each metric a <wishbone.event.Metric>
        datastructure is created and stored in the @data part of
        <wishbone.event.Event>.


    Non-numeric values are ignored.

    For example:

        {"server": {"host01": {"memory": {"free": 10, "consumed": 90}}}}

        Would generate following metrics:

        server.host01.memory.free
        server.host01.memory.consumed

    These metrics are converted to the Wishbone metric data format:

        http://wishbone.readthedocs.org/en/latest/logs%20and%20metrics.html#format

    The module is expecting a Python <dict> type.  That means you should have
    already decoded the incoming data using a module like wishbone.decode.json.


    Parameters:

        - source(str)("@data")
           |  The event field containing the data to convert.

        - type(str)("wishbone")
           |  An arbitrary string to assign to the "type" field of the Metric
           |  datastructure.

        - metric_source(str)("wishbone")
           |  An arbitrary string to assign to the "source" field of the Metric
           |  datastructure.

        - tags(set)()
           |  An arbitrary set of tags assign to the "tags" field of the Metric
           |  datastructure.


    Queues:

        - inbox:    Incoming events.

        - outbox:   Outgoing events with @data containing the wishbone.event.Metric data.
    '''

    def __init__(self, actor_config, source="@data", type="wishbone", metric_source="wishbone", tags=()):
        Actor.__init__(self, actor_config)

        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.pool.createQueue("outbox")

    def consume(self, event):

        data = event.get(self.kwargs.source)

        if isinstance(data, dict) or isinstance(data, list):
            for name, value in self.recurseData(data):
                metric = Metric(time(), self.kwargs.type, self.kwargs.metric_source, name, value, "", self.kwargs.tags)
                self.submit(Event(metric), self.pool.queue.outbox)
        else:
            raise Exception("Dropped incoming data because not of type <dict>. Perhaps you forgot to feed the data through wishbone.decode.json first?")

    def recurseData(self, data, breadcrumbs=""):

        if isinstance(data, list):
            for item in data:
                for a, b in self.recurseData(item, breadcrumbs):
                    yield a, b
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                name = self.__concatBreadCrumbs(breadcrumbs, key)
                for a, b in self.recurseData(value, name):
                    yield a, b
        elif isinstance(data, bool):
            pass
        elif isinstance(data, (int, long, float)):
            yield breadcrumbs, data

    def __concatBreadCrumbs(self, breadcrumbs, element_name):

        if element_name.startswith('.'):
            element_name = "_%s" % (element_name[1:])
        if element_name.startswith('_'):
            element_name = "_%s" % (element_name)

        name = "%s.%s" % (breadcrumbs, element_name)

        if name.startswith('.'):
            return name[1:]
        else:
            return name
