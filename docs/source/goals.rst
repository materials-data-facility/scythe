Project Goals
=============

The goal of MaterialsIO is to minimize the amount of code duplication between data-driven materials software codes.
Many materials databases at present rely on custom software to extract information from scientific files and transform that data into a standardized format.
Further, automation or analysis software requires extracting information from files.
While the data needs of application vary, they all rely on similar algorithms to extract information from the same types of files.
*MaterialsIO is designed to be a shared repository for these algorithms*.

The core of MaterialsIO is a collection of "parsers" which each generate simplified, standardized data from a certain class of files.
For example, the :class:`ElectronMicroscopyParser` produces structured data from file types specific to brands of electron microscopes.

The parsers do not necessarily generate data in a format needed by any tool.
Rather, the parsers are designed to produce *all* of the information needed by all projects that utilitize the libraries.
In this way, the parsers can service every user without modification.

What Does MaterialsIO *Do*?
---------------------------

MaterialsIO is designed to provide the answer to two limited questions:

1. *Which files can I parse with a certain tool?*
    MaterialsIO provides tools for quickly finding files of a certain type

2. *What information does a set of files contain?*
    MaterialsIO provides a library of tools that transform data into a simpler formats

What Does MaterialsIO *Not Do*?
-------------------------------

There are several questions that are specifically out-of-scope for MaterialsIO:

1. *How do I get access to files that I want to parse?*
    MaterialsIO does not solve the data transfer problem
2. *How can I parse large numbers of files reliably?*
    MaterialsIO is not a distributed workflow engine, but is designed to intregrate
    with one for extracting metadata from large filesystems.
3. *How can I translate data into the schema needed for my application?*
    The goal of MaterialsIO is to go from opaque to well-documented formats.
    We recommend implementing separate "adapter" classes to transform MaterialsIO metadata to your specific requirements.

See our `"how to use MaterialsIO" documentation <user-guide.html#integrating-materialsio-into-applications>`_ for more detail
on how to integrate MaterialsIO into an application that provides these intentionally-missing features.
