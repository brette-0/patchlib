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

-  *Intended for Python 3.7 and above*
-  Uses
   `importlib <https://docs.python.org/3/library/importlib.html>`__
   for complete importing
-  Currently can only use ``ips`` files.

+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| Name   | package                                                                                                    | Docs                                         | Version | Size       | Docs                           |
+========+============================================================================================================+==============================================+=========+============+================================+
| IPS    | `patchlib.ips <https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/ips/__init__.py>`_ | :doc:`patchlib.ips_docs </package_docs/ips>` | 1.0     | ``17KB``   | :doc:`IPS <filetype_docs/ips>` |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+
| BPS    | ``patchlib.bps``                                                                                           | Not yet                                      | alpha   | ``5.85KB`` | None                           |
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
| Luna   | ``patchilb.luna``                                                                                          | Not yet                                      | None    | None       | None                           |
+--------+------------------------------------------------------------------------------------------------------------+----------------------------------------------+---------+------------+--------------------------------+

Using ``import patchlib`` will install all packages with the
``importlib`` module. ``patchlib`` provides no context abundant methods
and relies on the package being specified.

``Luna`` serialized class handling may be implemented at a later point
in time once enough of the crucial patch filetypes have been completed.

`docs <https://github.com/BrettefromNesUniverse/patchlib/tree/main/docs>`__
applies only to the `working
build <https://pypi.org/project/patchlib/>`__\  *and therefore may not
reflect the* `open source
versions <https://github.com/BrettefromNesUniverse/patchlib/blob/main/src/patchlib/>`_.
*Contributions are open an encouraged, and will be release once the open build leaves exerpiment phase.*

In either ``cmd`` or ``powershell`` for Windows, and ``terminal`` for Posix/Unix Systems.

.. note:: 
   Currently only ``patchlib.ips`` is implemented, we are already working the next subpackage however and welcome contributions

.. toctree::
   :maxdepth: 2
   :caption: Subpackage Documentation:
   :hidden:

   package_docs/ips

.. toctree::
   :maxdepth: 2
   :caption: Filetype Documentation:
   :hidden:

   filetype_docs/ips

.. toctree::
   :maxdepth: 2
   :caption: Information:
   :hidden:

   Information/author
   Information/faq
   Information/resources
