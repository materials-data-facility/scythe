User Guide
==========

In this part of the guide, we show a simple example of using a Scythe parser and discuss the
full functionality of a parser.

Installing Scythe (for users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing Scythe should be as easy as a single ``pip`` command. Assuming you have a
version of Python that is 3.8 or higher, running::

    pip install git+https://github.com/materials-data-facility/Scythe.git

Should get the basics of Scythe installed. By default however, only a small subset of
parsers will be installed (this is done so you do not need to install all the dependencies of
parsers you may never use). To install additional parsers, you can specify "extras" at install time
using the ``[...]`` syntax for ``pip``. For example, if you want to install all the parsers
bundled with Scythe (and their dependencies), run::

    pip install "git+https://github.com/materials-data-facility/Scythe.git#egg=scythe[all]"

This will pull in many more packages, but also enable as many parsers as possible. Check the list
under ``[tool.poetry.extras]`` in ``pyproject.toml`` to see all the options you can specify in
the brackets of the ``pip install`` command.

.. note:: In the *hopefully* near future, Scythe should be published on
    `PyPI <https://pypi.org>`_ (see
    `this Github issue <https://github.com/materials-data-facility/Scythe/issues/42>`_ for
    updates), meaning install should be easier via a simple ``pip install scythe`` or
    ``pip install scythe[all]``, rather than having to specify the Git URL as in the above
    example

Discovering a Parser
~~~~~~~~~~~~~~~~~~~~

Scythe uses `stevedore <https://docs.openstack.org/stevedore/latest/index.html>`_ to manage
a collection of parsers, and has a utility function for listing available parsers::

    from scythe.utils.interface import get_available_parsers
    print(get_available_parsers())

This snippet will print a dictionary of parsers installed on your system. Both parsers that are
part of the Scythe base package and those defined by other packages will be included in this
list.

Simple Interface
~~~~~~~~~~~~~~~~

The methods in :mod:`scythe.utils.interface` are useful for most applications. As an
example, we illustrate the use of :class:`scythe.file.GenericFileParser`, which is
available through the ``'generic'`` parser plugin::

    from scythe.utils.interface import execute_parser
    print(execute_parser('generic', ['pyproject.toml']))


The above snippet creates the parser object and runs it on a file named ``pyproject.toml``. Run
in the root directory of the Scythe, it would produce output similar to the following,
likely with a different ``sha512`` value if the contents of that file have changed since this
documentation was written:

.. code:: json

    [{
        "data_type": "ASCII text",
        "filename": "pyproject.toml",
        "length": 2421,
        "mime_type": "text/plain",
        "path": "pyproject.toml",
        "sha512": "a7eb382c4a3e6cf469656453f9ff2e3c1ac2c02c9c2ba31c3d569a09883e2b2471801c39125dafb7c13bfcaf9cf6afbab92afa4c053c0c93a4c8c59acad1b85b"
    }]

The other pre-built parsing function provides the ability to run all parsers on all files in a
directory::

    from scythe.utils.interface import run_all_parsers
    gen = run_all_parsers('.')
    for record in gen:
        print(record)

A third route for using ``scythe`` is to employ the ``get_parser`` operation to access a
specific parser, and then use its class interface (described below)::

    from scythe.utils.interface import get_parser
    parser = get_parser('generic')
    gen = parser.parse_directory('.')
    for record in gen:
        print(record)


Advanced Usage: Adding Context
++++++++++++++++++++++++++++++

The function interface for Scythe supports using "context" and "adapters" to provide
additional infomration to a parser or change the output format, respectively. Adapters are
described in `Integrating Scythe into Applications <#id1>`_. Here, we describe the purpose
of context and how to use it in our interface.

Context is information about the data held in a file that is not contained within the file itself
. Examples include human-friendly descriptions of columns names or which values actually
represent a missing measurement in tabular data file (e.g., CSV files). A limited number of
parsers support context and this information can be provided via the ``execute_parser``
function::

    execute_parser('csv', 'tests/data/test.csv', context={'na_values': ['N/A']})


The types of context information used by a parser, if any, is described in the
`documentation for each parser <parsers.html>`_.

The ``run_all_parsers_on_directory`` function has several options for providing context to the
parsers. These options include specifying "global context" to be passed to every parser or
adapter and ways of limiting the metadata to specific parsers. See
:meth:`scythe.utils.interface.run_all_parsers_on_directory` for further details on the
syntax for this command.

.. note::

    *Context is still an experimental feature and APIs are subject to change*


Class Interface
~~~~~~~~~~~~~~~

The class API of parsers provide access to more detailed features of individual parsers. The
functionality of a parser is broken into several simple operations.

Initializing a Parser
+++++++++++++++++++++

The first step to using a Parser is to initialize it. Most parsers do not have any options for
the initializer, so you can create them with::

    parser = Parser()

Some parsers require configuration options that define how the parser runs, such as the location
of a non-Python executable.

Parsing Method
++++++++++++++

The main operation for any parser is the data extraction operation: ``parse``.

In most cases, the ``parse`` operation takes the path to a file and and returns a summary of the
data the file holds::

    metadata = parser.parse(['/my/file'])

Some parsers take multiple files that describe the same object (e.g., the input and output files
of a simulation) and use them to generate a single metadata record::

    metadata = parser.parse(['/my/file.in', '/my/file.out'])

The `grouping method <#grouping-files>`_ for these parsers provides logic to identify groups of
related files.

Some parsers also can use information that is not contained within the file themselves, which can
be provided to the parser as a "context"::

    metadata = parser.parse(['/my/file1'], context={'headers': {'temp': 'temperature'}})

The documentation for the parser should indicate valid types of context information.

Grouping Files
++++++++++++++

Parsers also provide the ability to quickly find groups of associated files: ``group``.
The ``group`` operation takes path or list of files and, optionally, directories and generates
a list of files that should be treated together when parsing::

    parser.group(['input.file', 'output.file', 'unrelated']) # -> [('input.file', 'output.file'), ('unrelated',)]

Parsing Entire Directories
++++++++++++++++++++++++++

``scythe`` also provides a utility operation to parse all groups of valid files in a directory::

    metadata = list(parser.parse_directory('.'))

``parse_directory`` is a generator function, so we use ``list`` here to turn the output into a list
format.

Attribution Functions
+++++++++++++++++++++

Two functions, ``citations`` and ``implementors``, are available to determine who contirbuted a
parser. ``implementors`` returns the list of people who created a parser, who are likely the
points-of-contact for support. ``citations`` indicates if any publications are available that
describe the underlying methods and should be reference in scientific articles.

Full Parser API
+++++++++++++++

The full API for the parsers are described as a Python abstract class:

.. autoclass:: scythe.base.BaseParser
    :members:
    :member-order: bysource

Integrating Scythe into Applications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scythe is designed to create a documented, JSON-format version of scientific files, but
these files might not yet be in a form useful for your application. We recommend an "adapter"
approach to post-process these "generic JSON" files that can actually be used for your application.

BaseAdapter
+++++++++++

The ``BaseAdapter`` class defines the interface for all adapters.

.. autoclass:: scythe.adapters.base.BaseAdapter
    :member-order: bysource
    :noindex:
    :members:

Adapters must fulfill a single operation, ``transform``, which renders metadata from one of the
Scythe parsers into a new form. There are no restrictions on the output for this function,
except that ``None`` indicates that there is no valid transformation for an object.

The ``check_compatibility`` and ``version`` method provide a route for marking which versions of
a parser are compatible with an adapter. ``scythe`` uses the version in utility operations
to provide warnings to users about when an adapter is out-of-date.

Using Adapters
++++++++++++++

The same utility operations `described above <#simple-interface>`_ support using adapters. The
``execute_parser`` function has an argument, ``adapter``, that takes the name of the adapter as
an input and causes the parsing operation to run the adapter after parsing. The
``run_all_parsers`` function also has arguments (e.g., ``adapter_map``) that associate each
parser with the adapter needed to run after parsing.

As an example, we will demonstrate an adapter that comes packaged with Scythe:
:class:`scythe.adapters.base.SerializeAdapter`
The serialize adapter is registered using ``stevedore`` as the name "serialize". To use it after
all parsers::

    from scythe.utils.interface import run_all_parsers
    gen = run_all_parsers('.', default_adapter='serialize')

Implementing Adapters
+++++++++++++++++++++

Any new adapters must inherit from the ``BaseAdapter`` class defined above. You only need
implement the ``transform`` operation.

Once the adapter is implemented, you need to put it in a project that is installable via pip. See
[python docs](https://docs.python.org/3.7/distutils/setupscript.html) for a detailed tutorial or
copy the structure used by the
`MDF's adapter library <https://github.com/materials-data-facility/mdf-materialsio-adapters>`_.

Then, register the adapter with ``stevedore`` by adding it as an entry point in your project's
``setup.py`` or ``pyproject.toml`` file. See the
`stevedore documentation for more detail <https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html#registering-the-plugins>`_.
We recommend using the same name for a adapter as the parser it is designed for so that
``scythe`` can auto-detect the adapters associated with each parser.

Examples of Tools Using Scythe
+++++++++++++++++++++++++++++++++++

Materials Data Facility:
https://github.com/materials-data-facility/mdf-materialsio-adapters
