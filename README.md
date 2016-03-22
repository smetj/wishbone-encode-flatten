
              __       __    __
    .--.--.--|__.-----|  |--|  |--.-----.-----.-----.
    |  |  |  |  |__ --|     |  _  |  _  |     |  -__|
    |________|__|_____|__|__|_____|_____|__|__|_____|
                                       version 2.1.2

    Build composable event pipeline servers with minimal effort.


    =======================
    wishbone.encode.flatten
    =======================

    Version: 0.1.0

    Flattens a dict structure of arbitrary depth into individual metric events.
    ---------------------------------------------------------------------------


        This module takes a <dict> structure and recursively travels it flattening
        the namespace into a dotted format untill a numeric value is encountered.
        For each metric a <wishbone.event.Metric> datastructure is created.

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

            - type(str)("wishbone")
               |  An arbitrary string to assign to the "type" field of the Metric
               |  datastructure.

            - source(str)("wishbone")
               |  An arbitrary string to assign to the "source" field of the Metric
               |  datastructure.

            - tags(set)()
               |  An arbitrary set of tags assign to the "tags" field of the Metric
               |  datastructure.


        Queues:

            - inbox:    Incoming events.

            - outbox:   Outgoing events with @data containing the wishbone.event.Metric data.

