.. image:: logo.png
.. title:: patchlib

``patchlib`` is a library of tools for total control of the fundamental
elements of each ``patch`` filetype, and is split into several packages,
each documented in detail in this repository, and installed on:
`PyPi <https://pypi.org/project/patchlib/>`__

Or can be installed with:

============================ =============================
Windows                      Posix / Unix
============================ =============================
``pip install get_patchlib`` ``pip3 install get_patchlib``
============================ =============================

-  **Intended for Python 3.7 and above**
-  Uses
   `importlib <https://docs.python.org/3/library/importlib.html>`__
   for complete importing
-  Uses `zlib <https://docs.python.org/3/library/zlib.html>`__ for ``bps`` `Checksum Validation <https://en.wikipedia.org/wiki/Checksum>`__
-  Currently can only use ``ips`` and ``bps`` files.

+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| Name   | package                                                                                                    | Docs                                         | Version | Size       | Docs                           |
+========+============================================================================================================+==============================================+=========+============+================================+
| IPS    | `patchlib.ips <https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips.py>`_          | :doc:`patchlib.ips_docs </package_docs/ips>` | 1.0     | ``17KB``   | :doc:`IPS <filetype_docs/ips>` |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| BPS    | `patchlib.ips <https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips.py>`_          | :doc:`patchlib.bps_docs </package_docs/bps>` | 0.6     | ``16KB``   | :doc:`BPS <filetype_docs/bps>` |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| Xdelta | ``patchlib.xdelta``                                                                                        | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| PPF    | ``patchlib.ppf``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| UPS    | ``patchlib.ups``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| APS    | ``patchlib.aps``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| RUP    | ``patchlib.rup``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| NPS    | ``patchlib.nps``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| EPS    | ``patchlib.eps``                                                                                           | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+

Using ``import patchlib`` will install all packages with the
``importlib`` module. ``patchlib`` provides no context abundant methods
and relies on the package being specified.

`docs <https://github.com/BrettefromNesUniverse/patchlib/tree/main/docs>`__
applies only to the `working
build <https://pypi.org/project/patchlib/>`__\  *and therefore may not
reflect the* `open source
versions <https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/>`_.

.. note:: 
   ``patchlib.bps`` is not fully tested and some features remain unimplemented.

.. note:: 
   ``patchlib.eps`` some installs contain leftover ``eps`` code which should not be used.

.. toctree::
   :maxdepth: 2
   :caption: Subpackage Documentation:
   :hidden:

   package_docs/ips
   package_docs/bps

.. toctree::
   :maxdepth: 2
   :caption: Filetype Documentation:
   :hidden:

   filetype_docs/ips
   filetype_docs/bps

.. toctree::
   :maxdepth: 2
   :caption: Information:
   :hidden:

   Information/author
   Information/faq
   Information/resources
