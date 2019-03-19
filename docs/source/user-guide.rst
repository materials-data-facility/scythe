User Guide
==========

In this part of the guide, we show a simple example of using a MaterialsIO parser
and discuss the full functionality of a parser.

Example Usage
~~~~~~~~~~~~~

As an example, we illustrate the use of ``FileParser``, a parser that returns status information about a file::

    parser = FileParser()
    parser.parse(['setup.py'])

.. todo:: Actually implement ``FileParser``

The above snippet creates the parser object and runs it on a file named ``setup.py``.
Run in the root directory of the MaterialsIO it would produce output similar to:

.. code:: json

    {
        "modification_time": 453
    }


The ``parse`` operation evaluates a file or group of files that describe a single logical object (e.g., a simulation).
Running on the parser on every file in a directory is accomplished by the ``group`` method::

    metadata = [parser.parse(x) for x in parser.group('.')]

The ``group`` operation evaluates every file in the listed directory and its subdirectories,
and generates groupings of files that likely describe the same object.
Grouping is unnecessary for ``FileParser``, which treats each file individually.
Grouping is necessary in cases where an object is described by multiple objects (e.g., the inputs and output files for a simulation).


Another potential problem with the script about is that some files may not be compatible with the parser.
The MaterialsIO parsers provide a ``is_valid`` operation that determines whether a specific grouping of
files is actually compatible with a parser::

    metadata = [parser.parse(x) for x in parser.group('.') if parser.is_valid(x)]

The above function returns a list of all metadata that is possible to extract from a directory.
For convenience, we provide a utility operation to parse all the files in a directory::

    metadata = parser.parse_directory('.')

.. todo:: We need an example parser to evaluate grouping functionality

.. todo:: Provide a utility operation for running on a whole directory.

    That utility could even determine whether a parser has overloaded the default ``is_valid`` operation
    and use that to assess whether it will actually use ``is_valid`` or just attempt parsing inside of
    a try/except block.


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

Compatibility Checking
----------------------

Parsers also provide a method for checking whether a group of files is compatible with it:: `is_valid`.
These ``is_valid`` method take a list of the files in a certain group as input and, optionally,
context information about the files::

    parser.is_valid(['/my/file'])

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
