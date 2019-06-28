User Guide
==========

In this part of the guide, we show a simple example of using a MaterialsIO parser
and discuss the full functionality of a parser.

Discovering a Parser
~~~~~~~~~~~~~~~~~~~~

MaterialsIO uses `stevedore <https://docs.openstack.org/stevedore/latest/index.html>`_ to manage a collection of parsers,
and has a utility function for listing available parsers::

    from materials_io.utils import get_available_parsers
    print(get_available_parsers())

This snippet will print a dictionary of parsers installed on your system.
Both parsers that are part of the MaterialsIO base package will be installed,

Example Usage
~~~~~~~~~~~~~

As an example, we illustrate the use of ``GenericFileParser``, a parser that returns basic status and type information about a file::

    parser = GenericFileParser()
    parser.parse(['setup.py'])


The above snippet creates the parser object and runs it on a file named ``setup.py``.
Run in the root directory of the MaterialsIO, it would produce output similar to:

.. code:: json

    [{
        "mime_type": "text/x-python",
        "length": 623,
        "filename": "setup.py",
        "hash": "[...]"
    }]


The ``parse`` operation generates a single summary from a file or, in advanced cases, a group of files that describe the same object (e.g., a simulation).
The ``group`` operation identifies these sets of files files::

    metadata = [parser.parse(x) for x in parser.group(['setup.py', 'requirements.txt'])]

The ``group`` operation for ``GenericFileParser`` places each file in its own group, because they are all treated separately.
More advanced parsers identify groupings of files that describe the same object (e.g., the input and output files of the same simulation),
and may only generate groups from files that are likely to be compatible with the parser.

For convenience, we provide a utility operation to parse all the files in a directory::

    metadata = list(parser.parse_directory('.'))

``parse_directory`` is a generator function, so we use ``list`` to turn the output into a list format.


Parser Interface
~~~~~~~~~~~~~~~~

The functionality of a parser is broken into several simple operations.

Initializing a Parser
---------------------

The first step to using a Parser is to initialize it.
Most parsers do not have any options for the initializer, so you can create them with::

    parser = Parser()

Some parsers require configuration options that define how the parser runs,
such as the location of a non-Python executable.

Parsing Method
--------------

The main operation for any parser is the data extraction operation: ``parse``.

In most cases, the ``parse`` operation takes the path to a file and
and returns a summary of the data the file holds::

    metadata = parser.parse_files(['/my/file'])

Some parsers take multiple files that describe the same object (e.g., the input and output files of a simulation)
and use them to generate a single metadata record::

    metadata = parser.parse_files(['/my/file.in', '/my/file.out'])

The `grouping method <#grouping-files>`_ for these parsers provides logic to identify groups of related files.

Some parsers also can use information that is not contained within the file themselves, which can be provided to the parser as a "context"::

    metadata = parser.parse_files(['/my/file1'], context={'headers': {'temp': 'temperature'}})

The documentation for the parser should indicate valid types of context information.

Grouping Files
--------------

Parsers also provide the ability to quickly find groups of associated files: ``group``.
The ``group`` operation takes path or list of paths as input and generates candidate groups of files::

    parser.group('/data/directory')

Attribution Functions
---------------------

Two functions, ``citations`` and ``implementors``, are available to determine who contirbuted a parser.
``implementors`` returns the list of people who created a parser, who are likely the points-of-contact for support.
``citations`` indicates if any publications are available that describe the underlying methods and should be reference
in scientific articles.


Full Parser API
---------------

The full API for the parsers are described as a Python abstract class:

.. autoclass:: materials_io.base.BaseParser
    :members:
    :member-order: bysource

Integrating MaterialsIO into Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: Write this section

    Waiting to discuss with Tyler, Max, and Jonathon
