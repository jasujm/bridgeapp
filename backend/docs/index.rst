.. bridgeapp documentation master file, created by
   sphinx-quickstart on Sun Jun  7 22:33:17 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
Welcome to bridgeapp's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


================
Module reference
================

Model definitions
-----------------

The :mod:`bridgeapp.bridgeprotocol.models` module contains the model definitions
needed across the application.

.. automodule:: bridgeapp.bridgeprotocol.models
   :members:

Bridge protocol implementation
------------------------------

Classes and utilities for communicating with the bridge backend server.

Bridge client
.............

The :class:`bridgeapp.bridgeprotocol.BridgeClient` class is the main class used
for sending commands and receiving replied from the server.

.. autoclass:: bridgeapp.bridgeprotocol.BridgeClient
   :members:

Events
......

:class:`bridgeapp.bridgeprotocol.BridgeEventReceiver` is used to receive
asynchronous events (:class:`bridgeapp.bridgeprotocol.BridgeEvent` instances)
from the server

.. autoclass:: bridgeapp.bridgeprotocol.BridgeEvent

.. autoclass:: bridgeapp.bridgeprotocol.BridgeEventReceiver
   :members:

Miscellaneous
.............

.. automodule:: bridgeapp.bridgeprotocol.exceptions
   :members:

.. automodule:: bridgeapp.bridgeprotocol.utils
   :members:

REST API
--------

The implementation of the REST API. The API allows HTTP and WebSocket clients to
communicate with a bridge backend server which uses the low level bridge
protocol.

.. automodule:: bridgeapp.api.utils
   :members:
