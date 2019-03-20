Contributor Guide
=================

This part of the MaterialsIO guide details how to add a new parser to the ecosystem.

Step 1: Implement a Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating a new parser is accomplished by implementing the `BaseParser <user-guide.html#parser-api>`_ abstract class.
If you are new to MaterailsIO, we recommend reviewing the `User Guide <user-guide.html#available-methods>`_ first to learn about the available methods of BaseParser.
Minimally, you need only implement the ``parse``, ``version``, and ``implementors`` operations of these
Each of these methods (and any other methods you override) must be stateless, so that running the operation does not change the behavior of the parser.

Class Attributes
----------------

The ``BaseParser`` class supports configuration options as Python class attributes.
These options are intended to define the behavior of a parser for a particular environment
(e.g., paths of required executables) or for a particular application (e.g., turning off unneeded features).
We recommend limiting these options to be only JSON-serializable data types and for all to be defined in the ``__init__`` function to simplify text-based configuration files.

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
    Deviating from already existing formats complicates later modifications to a parser.


Beyond recommendations about the data type, we have a recommendations for the parser behavior:

#. *Fail loudly and as specifically as possible*
    Parsers should return exceptions when provided incompatible data and not fail by returning data.
    Provide an error message that indicates whether the file is incompatible, or the parser is misconfigured (e.g., missing a required library).

#. *Avoid configuration options that change only output format*
    Parsers can take configuration options that alter the output format, but configurations should be used sparingly.
    A good use of configuration would be to disable complex parsing operations if unneeded.
    A bad use of configuration would be to change the output to match a different schema.
    Operations that significantly alter the form but not the content of a summary should be implemented as adaptors.

#. *Context should not be required*
    Parsers can use additional context about files to genreate summaries, but this information should not be required.
    Settings that are identical for each file could be better suited as configuration settings.

Implementing ``is_valid``
----------------------

The ``is_valid`` operation is used to determine whether a set of files are compatible with the parser.
Implementing it is optional and recommended only when there are fast ways of testing file types.
The default implementation is to call ``parse`` and see if the parser fails.
``is_valid`` should return ``False`` for incompatible files and only throw Exceptions if the parser is misconfigured.


Implementing ``group``
----------------------

The ``group`` operation finds all groups of files in a directly that should be treated as related units.
Implementing ``group`` is optional.
The default implementation is to return each file in the directory as its own group.
New implementations of ``group`` need not return every file as part of a group (e.g., it can perform compatibility filtering)
and files are allowed to appear in more than 1 group.
In general, our recommendation is to return all possible groupings of files when in doubt and let the ``is_valid`` and ``parse`` operations sort out which groupings are valid.

Implementing ``citations`` and ``implementors``
-----------------------------------------------

The ``citation`` and ``implementors`` methods identify additional resources describing a parser and provide credit to contributors.
``implementors`` is required, as this operation is also used to identify points-of-contact for support requests.

Implementing ``version``
------------------------

We require using `semantic versioning <https://semver.org/>`_ for specifying the version of parsers.
As the API of the parser should remain unchanged, use versioning to indicate changes in available options or the output schema.
The ``version`` operation should return the version of the parser.
