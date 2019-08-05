Contributor Guide
=================

This part of the MaterialsIO guide details how to add a new parser to the ecosystem.

Step 1: Implement the Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a new parser is accomplished by implementing the `BaseParser <user-guide.html#parser-api>`_ abstract class.
If you are new to MaterailsIO, we recommend reviewing the `User Guide <user-guide.html#available-methods>`_ first to learn about the available methods of BaseParser.
Minimally, you need only implement the ``parse``, ``version``, and ``implementors`` operations for a new parser.
Each of these methods (and any other methods you override) must be stateless, so that running the operation does not change the behavior of the parser.

We also have subclasses of ``BaseParser`` that are useful for common types of parsers:

- ``BaseSingleFileParser``: Parsers that only ever evaluate a single file at a time

Class Attributes and Initializer
--------------------------------

The ``BaseParser`` class supports configuration options as Python class attributes.
These options are intended to define the behavior of a parser for a particular environment
(e.g., paths of required executables) or for a particular application (e.g., turning off unneeded features).
We recommend limiting these options to be only JSON-serializable data types and for all to be defined in the ``__init__`` function to simplify text-based configuration files.

The initializer function should check if a parser has access to all required external tools, and throw exceptions if not.
For example, a parser that relies on calling an external command-line tool should check whether the package is installed.
In general, parsers should fail during initialization and not during the parsing operation if the system in misconfigured.

Implementing ``parse``
----------------------

The ``parse`` method contains the core logic of a MaterialsIO parser: rendering a summary of a group of data files.
We do not specify any particular schema for the output but we do recommend best practices:


#. *Summaries must be JSON-serializable.*
    Limiting to JSON data types ensures summaries are readable by most software without special libraries.
    JSON documents are also able to be documented easily.

#. *Human-readability is desirable.*
    JSON summaries should be understandable to users without expert-level knowledge of the data.
    Avoid unfamiliar acronyms, such as names of variables in a specific simulation code or settings specific to a certain brand of instrument.

#. *Adhere closely to the original format.*
    If feasible, try to stay close to the original data format of a file or the output of a library used for parsing.
    Deviating from already existing formats complicates modifications to a parser.

#. *Always return a dictionary.*
    If a parser can return multiple records from a single file group, return the list as an element of the dictionary.
    Any metadata that pertains to each of the sub-records should be stored as a distinct element
    rather than being duplicated in each sub-record.


We also have a recommendations for the parser behavior:

#. *Avoid configuration options that change only output format.*
    Parsers can take configuration options that alter the output format, but configurations should be used sparingly.
    A good use of configuration would be to disable complex parsing operations if unneeded.
    A bad use of configuration would be to change the output to match a different schema.
    Operations that significantly alter the form but not the content of a summary should be implemented as adaptors.

#. *Consider whether context should be configuration.*
    Settings that are identical for each file could be better suited as configuration settings than as context.

Implementing ``group``
----------------------

The ``group`` operation finds all sets of files in a user-provided of paths list that should be parsed together.
Implementing ``group`` is optional.
Implementing a new ``group`` method is required only when the default behavior of "each file is its own group"
(i.e., the parser only treats files individually) is incorrect.

Files are allowed to appear in more than one group,
but we recommend generating only the largest valid group of files to minimize the same metadata being generated multiple times.

It is important to note that that file groups are specific to a parser.
Groupings of files that are meaningful to one parser need not be meaningful to another.
For that reason, limit the definition of groups to sets of files that can be parsed together
without consideration to what other information makes the files related (e.g., being in the same directory).

Another appropriate use of the ``group`` operation is to filter out files which are very unlikely to parse correctly.
For example, a PDF parser could identify only files with a ".pdf" extension.

Implementing ``citations`` and ``implementors``
-----------------------------------------------

The ``citation`` and ``implementors`` methods identify additional resources describing a parser and provide credit to contributors.
``implementors`` is required, as this operation is also used to identify points-of-contact for support requests.

``citation`` should return a list of BibTeX-format references.

``implementors`` should return a list of people and, optionally, their contract infomration
in the form: "FirstName LastName <email@provider.com>".

Implementing ``version``
------------------------

We require using `semantic versioning <https://semver.org/>`_ for specifying the version of parsers.
As the API of the parser should remain unchanged, use versioning to indicate changes in available options or the output schema.
The ``version`` operation should return the version of the parser.


Step 2: Document the Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The docstring for a parser must start with a short, one sentence summary of the parser,
which will be used by our autodocumentation tooling.
The rest of the documentation should describe what types of files are compatible,
what context infomration can be used, and
summarize what types of metadata are generated.

.. todo:: Actually write these descriptors for the available parsers

The MaterialsIO project uses JSON documents as the output for all parsers and `JSON Schema <https://json-schema.org/>`_ to describe the content of the documents.
The BaseParser class includes a property, ``schema``, that stores a description of the output format.
We recommend writing your description as a separate file and having the ``schema`` property read and output the contents of this file.
See the `GenericFileParser source code <https://github.com/materials-data-facility/MaterialsIO/blob/master/materials_io/file.py>`_ for a example.


Step 3: Register the Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Preferred Route: Adding the Parser to MaterialsIO
-------------------------------------------------

If your parser has the same dependencies as existing parsers, add it to the existing module with the same dependencies.

If your parser has new dependencies, create a new module for your parser in ``materials_io``, and then add the requirements as a new key in the ``extras_require`` dictionary of ``setup.py`` and the ``requirements.txt`` file.
Next, add your parser to ``docs/source/parsers.rst`` by adding an ``.. automodule::`` statement that refers to your new module.

MaterialsIO uses stevedore to simplify access to the parsers.
After implementing and documenting the parser, add it to the ``entry_points`` section of the ``setup.py`` file for MaterialsIO.
See `stevedore documentation for more information <https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html#registering-the-plugins>`_.


Alternative Route: Including Parsers from Other Libraries
---------------------------------------------------------

If a parser would be better suited as part of a different library, you can still register it as a parser with MaterialsIO by altering your ``setup.py`` file.
Add an entry point with the namespace ``"materialsio.parser"`` and point to the class object following the
`stevedore documentation <https://docs.openstack.org/stevedore/latest/user/tutorial/creating_plugins.html#registering-the-plugins>`_.
Adding the entry point will let MaterialsIO use your parser if your librart is installed in the same Python environment as MaterialsIO.

.. todo:: Provide a public listing of materials_io-compatible software.

    So that people know where to find these external libraries
