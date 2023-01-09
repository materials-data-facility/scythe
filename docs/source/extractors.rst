Available Extractors
====================

These pages detail all of the extractors currently available in Scythe.

Quick Summary
~~~~~~~~~~~~~

The extractors that are configured to work with the stevedore plugin are:

.. list-plugins:: scythe.extractor


Detailed Listing
~~~~~~~~~~~~~~~~

Generic File Extractors
-----------------------

Extractors that work for any kind of file

.. automodule:: scythe.file
    :members:
    :exclude-members: implementors, schema, version, group

Image Extractors
----------------

Extractors that read image data

.. automodule:: scythe.image
    :members:
    :exclude-members: implementors, schema, version, group

Electron Microscopy Extractors
------------------------------

Extractors that read electron microscopy data of various sorts (images, spectra, spectrum images,
etc.) using the `HyperSpy <https://hyperspy.org>`_ package.

.. automodule:: scythe.electron_microscopy
    :members:
    :exclude-members: implementors, schema, version, group

Atomistic Data Extractors
-------------------------

Extractors related to data files that encode atom-level structure

.. automodule:: scythe.crystal_structure
    :members:
    :exclude-members: implementors, schema, version, group

.. automodule:: scythe.ase
    :members:
    :noindex:
    :exclude-members: implementors, schema, version, group

Calculation Extractors
----------------------

Extractors that retrieve results from calculations

.. automodule:: scythe.dft
    :members:
    :exclude-members: implementors, schema, version, group

.. automodule:: scythe.ase
    :members:
    :noindex:
    :exclude-members: implementors, schema, version, group

Structured Data Files
---------------------

Extractors that read data from structured files

.. automodule:: scythe.csv
    :members:
    :exclude-members: implementors, schema, version, group
