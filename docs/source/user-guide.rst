User Guide
==========

In this part of the guide, we show a simple example of using a MaterialsIO parser
and discuss the full functionality of a parser.

Discovering a Parser
~~~~~~~~~~~~~~~~~~~~

MaterialsIO uses `stevedore <https://docs.openstack.org/stevedore/latest/index.html>`_ to manage a collection of parsers,
and has a utility function for listing available parsers::

    from materials_io.util import get_available_parsers
    print(get_available_parsers())

This snippet will print a dictionary of parsers installed on your system.
Both parsers that are part of the MaterialsIO base package will be installed,

Example Usage
~~~~~~~~~~~~~

As an example, we illustrate the use of ``GenericFileParser``, a parser that returns status information about a file::

    parser = GenericFileParser()
    parser.parse(['setup.py'])


The above snippet creates the parser object and runs it on a file named ``setup.py``.
Run in the root directory of the MaterialsIO it would produce output similar to:

.. code:: json

    [{
        "mime_type": "text/x-python",
        "length": 623,
        "filename": "setup.py",
        "hash": "[...]"
    }]


The ``parse`` operation evaluates a file or group of files that describe a single object (e.g., a simulation).
Running on the parser on every file in a directory is accomplished by the ``group`` method::

    metadata = [parser.parse(x) for x in parser.group('.')]

The ``group`` operation generates a list of files in a certain directory that are likely to be compatible with a parser.
Further, some implementations of ``group`` identify groupings of files that describe the same object (e.g., the input and output files of the same simulation).
Both filtering files and grouping are unnecessary for ``FileParser``, which treats each file individually and works on any kind of file.

For convenience, we provide a utility operation to parse all the files in a directory::

    metadata = list(parser.parse_directory('.'))

``parse_directory`` is a generator function, so we use `list` to turn the output into a list format.

.. todo:: We need an example parser to evaluate grouping functionality


Available Methods
~~~~~~~~~~~~~~~~~

.. todo:: Is having two separate descriptions helpful?

The functionality of a parser is broken into several simple operations.

Initializing a Parser
---------------------

The first step to using a Parser is to initialize it.
Most parsers do not have any options for the initializer, so you can create them with::

    parser = Parser()

Some parsers require configuration options that define how the parser runs,
such as the location of a non-Python executable.

Parsing Methods
---------------

The main operation for any parser is the data extraction operation: ``parse``.
The ``parse`` operation takes a list of paths to files that collectively describe the same object (e.g., an experiment),
and returns a summary of the data the files hold::

    metadata = parser.parse_files(['/my/file1', '/my/file2'])

In some cases, you can provide information that is not contained within the file themselves, which can be provided to the parser as a "context"::

    metadata = parser.parse_files(['/my/file1'], context={'headers': {'temp': 'temperature'}})

Grouping Files
--------------

Parsers also provide the ability to quickly find groups of associated files: ``group``.
The ``group`` operation takes a directory as input and generates candidate groups of files::

    parser.group('/data/directory')

Attribution Functions
---------------------

Two functions, ``citations`` and ``implementors``, are available to determine who contirbuted a parser.
``implementors`` returns the list of people who created a parser, who are likely the points-of-contact for support.
``citations`` indicates if any publications are available that describe the underlying methods and should be reference
in scientific articles.


Parser API
----------

The full API for the parsers are described as a Python abstract class:

.. autoclass:: materials_io.base.BaseParser
    :members:
    :member-order: bysource

Integrating MaterialsIO into Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo:: Write this section

    Waiting to discuss with Tyler, Max, and Jonathon
