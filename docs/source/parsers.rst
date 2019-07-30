Available Parsers
=================

These pages detail all of the parsers currently available in MaterialsIO.

Quick Summary
~~~~~~~~~~~~~

The parsers that are configured to work with the stevedore plugin are:

.. list-plugins:: materialsio.parser


Detailed Listing
~~~~~~~~~~~~~~~~

Generic File Parsers
--------------------

Parsers that work for any kind of file

.. automodule:: materials_io.file
    :members:
    :exclude-members: implementors, schema, version, group

Image Parsers
-------------

Parsers that read image data (e.g., electron microscopy, computed tomography)

.. automodule:: materials_io.image
    :members:
    :exclude-members: implementors, schema, version, group

.. automodule:: materials_io.electron_microscopy
    :members:
    :exclude-members: implementors, schema, version, group

Atomistic Data Parsers
----------------------

Parsers related to data files that encode atom-level structure

.. automodule:: materials_io.crystal_structure
    :members:
    :exclude-members: implementors, schema, version, group

.. automodule:: materials_io.ase
    :members:
    :exclude-members: implementors, schema, version, group

Calculation Parsers
-------------------

Parsers that retrieve results from calculations

.. automodule:: materials_io.dft
    :members:
    :exclude-members: implementors, schema, version, group

.. automodule:: materials_io.ase
    :members:
    :exclude-members: implementors, schema, version, group

Structured Data Files
---------------------

Parsers that read data from structured files

.. automodule:: materials_io.csv
    :members:
    :exclude-members: implementors, schema, version, group
