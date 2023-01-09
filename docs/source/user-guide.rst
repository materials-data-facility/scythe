User Guide
==========

In this part of the guide, we show a simple example of using a Scythe extractor and discuss the
full functionality of an extractor.

Installing Scythe (for users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing Scythe should be as easy as a single ``pip`` command. Assuming you have a
version of Python that is 3.8 or higher, running::

    pip install scythe-extractors

Should get the basics of Scythe installed. By default however, only a small subset of
extractors will be installed (this is done so you do not need to install all the dependencies of
extractors you may never use). To install additional extractors, you can specify "extras" at install time
using the ``[...]`` syntax for ``pip``. For example, if you want to install all the extractors
bundled with Scythe (and their dependencies), run::

    pip install pip install scythe-extractors[all]

This will pull in many more packages, but also enable as many extractors as possible. Check the list
under ``[tool.poetry.extras]`` in ``pyproject.toml`` to see all the options you can specify in
the brackets of the ``pip install`` command.


Discovering an extractor
~~~~~~~~~~~~~~~~~~~~~~~~

Scythe uses `stevedore <https://docs.openstack.org/stevedore/latest/index.html>`_ to manage
a collection of extractors, and has a utility function for listing available extractors::

    from scythe.utils.interface import get_available_extractors
    print(get_available_extractors())

This snippet will print a dictionary of extractors installed on your system. Both extractors that are
part of the Scythe base package and those defined by other packages will be included in this
list.

Simple Interface
~~~~~~~~~~~~~~~~

The methods in :mod:`scythe.utils.interface` are useful for most applications. As an
example, we illustrate the use of :class:`scythe.file.GenericFileExtractor`, which is
available through the ``'generic'`` extractor plugin::

    from scythe.utils.interface import execute_extractor
    print(execute_extractor('generic', ['pyproject.toml']))


The above snippet creates the extractor object and runs it on a file named ``pyproject.toml``. Run
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

The other pre-built parsing function provides the ability to run all extractors on all files in a
directory::

    from scythe.utils.interface import run_all_extractors
    gen = run_all_extractors('.')
    for record in gen:
        print(record)

A third route for using ``scythe`` is to employ the ``get_extractor`` operation to access a
specific extractor, and then use its class interface (described below)::

    from scythe.utils.interface import get_extractor
    extractor = get_extractor('generic')
    gen = extractor.parse_directory('.')
    for record in gen:
        print(record)


Advanced Usage: Adding Context
++++++++++++++++++++++++++++++

The function interface for Scythe supports using "context" and "adapters" to provide
additional information Scythe into Applications <#id1>`_. Here, we describe the purpose
of context and how to use it in our interface.

Context is information about the data held in a file that is not contained within the file itself
. Examples include human-friendly descriptions of columns names or which values actually
represent a missing measurement in tabular data file (e.g., CSV files). A limited number of
extractors support context and this information can be provided via the ``execute_extractor``
function::

    execute_extractor('csv', 'tests/data/test.csv', context={'na_values': ['N/A']})


The types of context information used by an extractor, if any, is described in the
`documentation for each extractor <extractors.html>`_.

The ``run_all_extractors_on_directory`` function has several options for providing context to the
extractors. These options include specifying "global context" to be passed to every extractor or
adapter and ways of limiting the metadata to specific extractors. See
:meth:`scythe.utils.interface.run_all_extractors_on_directory` for further details on the
syntax for this command.

.. note::

    *Context is still an experimental feature and APIs are subject to change*


Class Interface
~~~~~~~~~~~~~~~

The class API of extractors provide access to more detailed features of individual extractors. The
functionality of an extractor is broken into several simple operations.

Initializing an extractor
+++++++++++++++++++++++++

The first step to using an extractor is to initialize it. Most extractors do not have any options for
the initializer, so you can create them with::

    extractor = Extractor()

Some extractors require configuration options that define how the extractor runs, such as the location
of a non-Python executable.

Parsing Method
++++++++++++++

The main operation for any extractor is the data extraction operation: ``parse``.

In most cases, the ``parse`` operation takes the path to a file and and returns a summary of the
data the file holds::

    metadata = extractor.parse(['/my/file'])

Some extractors take multiple files that describe the same object (e.g., the input and output files
of a simulation) and use them to generate a single metadata record::

    metadata = extractor.parse(['/my/file.in', '/my/file.out'])

The `grouping method <#grouping-files>`_ for these extractors provides logic to identify groups of
related files.

Some extractors also can use information that is not contained within the file themselves, which can
be provided to the extractor as a "context"::

    metadata = extractor.parse(['/my/file1'], context={'headers': {'temp': 'temperature'}})

The documentation for the extractor should indicate valid types of context information.

Grouping Files
++++++++++++++

Extractors also provide the ability to quickly find groups of associated files: ``group``.
The ``group`` operation takes path or list of files and, optionally, directories and generates
a list of files that should be treated together when parsing::

    extractor.group(['input.file', 'output.file', 'unrelated']) # -> [('input.file', 'output.file'), ('unrelated',)]

Parsing Entire Directories
++++++++++++++++++++++++++

``scythe`` also provides a utility operation to parse all groups of valid files in a directory::

    metadata = list(extractor.parse_directory('.'))

``parse_directory`` is a generator function, so we use ``list`` here to turn the output into a list
format.

Attribution Functions
+++++++++++++++++++++

Two functions, ``citations`` and ``implementors``, are available to determine who contirbuted a
extractor. ``implementors`` returns the list of people who created an extractor, who are likely the
points-of-contact for support. ``citations`` indicates if any publications are available that
describe the underlying methods and should be reference in scientific articles.

Full Extractor API
++++++++++++++++++

The full API for the extractors are described as a Python abstract class:

.. autoclass:: scythe.base.BaseExtractor
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
Scythe extractors into a new form. There are no restrictions on the output for this function,
except that ``None`` indicates that there is no valid transformation for an object.

The ``check_compatibility`` and ``version`` method provide a route for marking which versions of
an extractor are compatible with an adapter. ``scythe`` uses the version in utility operations
to provide warnings to users about when an adapter is out-of-date.

Using Adapters
++++++++++++++

The same utility operations `described above <#simple-interface>`_ support using adapters. The
``execute_extractor`` function has an argument, ``adapter``, that takes the name of the adapter as
an input and causes the parsing operation to run the adapter after parsing. The
``run_all_extractors`` function also has arguments (e.g., ``adapter_map``) that associate each
extractor with the adapter needed to run after parsing.

As an example, we will demonstrate an adapter that comes packaged with Scythe:
:class:`scythe.adapters.base.SerializeAdapter`
The serialize adapter is registered using ``stevedore`` as the name "serialize". To use it after
all extractors::

    from scythe.utils.interface import run_all_extractors
    gen = run_all_extractors('.', default_adapter='serialize')

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
We recommend using the same name for a adapter as the extractor it is designed for so that
``scythe`` can auto-detect the adapters associated with each extractor.

Examples of Tools Using Scythe
+++++++++++++++++++++++++++++++++++

Materials Data Facility:
https://github.com/materials-data-facility/mdf-materialsio-adapters
