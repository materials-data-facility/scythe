User Guide
==========

In this part of the guide, we show a simple example of using a MaterialsIO parser
and discuss the full functionality of a parser.

Discovering a Parser
~~~~~~~~~~~~~~~~~~~~

MaterialsIO uses `stevedore <https://docs.openstack.org/stevedore/latest/index.html>`_ to manage a collection of parsers,
and has a utility function for listing available parsers::

    from materials_io.utils.interface import get_available_parsers
    print(get_available_parsers())

This snippet will print a dictionary of parsers installed on your system.
Both parsers that are part of the MaterialsIO base package and those defined by other packages
will be included in this list.

Simple Interface
~~~~~~~~~~~~~~~~

The methods in :mod:`materials_io.utils.interface` are useful for most applications.
As an example, we illustrate the use of :class:`materials_io.generic.GenericFileParser`::

    from materials_io.utils.interface import execute_parser
    print(execute_parser('generic', ['setup.py']))


The above snippet creates the parser object and runs it on a file named ``setup.py``.
Run in the root directory of the MaterialsIO, it would produce output similar to:

.. code:: json

    [{
        "mime_type": "text/x-python",
        "length": 623,
        "filename": "setup.py",
        "hash": "[...]"
    }]

The other pre-built parsing function provides the ability to run all parsers on all files in a directory::

    from materials_io.utils.interface import run_all_parsers
    gen = run_all_parsers('.')
    for record in gen:
        print(record)

A third route for using ``materials_io`` is to employ the ``get_parser`` operation to access a specific
parser, and then use its class interface (described below)::

    from materials_io.utils.interface import get_parser
    parser = get_parser('generic')
    gen = parser.parse_directory('.')
    for record in gen:
        print(record)


Class Interface
~~~~~~~~~~~~~~~

The class API of parsers provide access to more detailed features of individual parsers.
The functionality of a parser is broken into several simple operations.

Initializing a Parser
+++++++++++++++++++++

The first step to using a Parser is to initialize it.
Most parsers do not have any options for the initializer, so you can create them with::

    parser = Parser()

Some parsers require configuration options that define how the parser runs,
such as the location of a non-Python executable.

Parsing Method
++++++++++++++

The main operation for any parser is the data extraction operation: ``parse``.

In most cases, the ``parse`` operation takes the path to a file and
and returns a summary of the data the file holds::

    metadata = parser.parse(['/my/file'])

Some parsers take multiple files that describe the same object (e.g., the input and output files of a simulation)
and use them to generate a single metadata record::

    metadata = parser.parse(['/my/file.in', '/my/file.out'])

The `grouping method <#grouping-files>`_ for these parsers provides logic to identify groups of related files.

Some parsers also can use information that is not contained within the file themselves, which can be provided to the parser as a "context"::

    metadata = parser.parse(['/my/file1'], context={'headers': {'temp': 'temperature'}})

The documentation for the parser should indicate valid types of context information.

Grouping Files
++++++++++++++

Parsers also provide the ability to quickly find groups of associated files: ``group``.
The ``group`` operation takes path or list of paths as input and generates candidate groups of files::

    parser.group('/data/directory')

Parsing Entire Directories
++++++++++++++++++++++++++

``materials_io`` also provides a utility operation to parse all groups of valid files in a directory::

    metadata = list(parser.parse_directory('.'))

``parse_directory`` is a generator function, so we use ``list`` to turn the output into a list format.

Attribution Functions
+++++++++++++++++++++

Two functions, ``citations`` and ``implementors``, are available to determine who contirbuted a parser.
``implementors`` returns the list of people who created a parser, who are likely the points-of-contact for support.
``citations`` indicates if any publications are available that describe the underlying methods and should be reference
in scientific articles.

Full Parser API
+++++++++++++++

The full API for the parsers are described as a Python abstract class:

.. autoclass:: materials_io.base.BaseParser
    :members:
    :member-order: bysource

Integrating MaterialsIO into Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: Write this section

    Waiting to discuss with Tyler, Max, and Jonathon
