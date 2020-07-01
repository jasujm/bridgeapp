.. bridgeapp documentation master file, created by
   sphinx-quickstart on Sun Jun  7 22:33:17 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bridgeapp's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Lightweight contract bridge webapp
==================================

.. include:: ../README.rst


Module reference
================

.. automodule:: bridgeapp.bridgeprotocol

.. autoclass:: bridgeapp.bridgeprotocol.BridgeClient
   :members:
   :inherited-members:

.. autoclass:: bridgeapp.bridgeprotocol.BridgeEventReceiver
   :members:
   :inherited-members:

.. automodule:: bridgeapp.bridgeprotocol.exceptions
   :members:

.. automodule:: bridgeapp.bridgeprotocol.utils
   :members:


Settings
========

.. pydantic:: bridgeapp.settings.Settings
