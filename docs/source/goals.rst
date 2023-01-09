Project Goals
=============

The goal of Scythe is to minimize the amount of code duplication between scientific databases.
Many databases rely on custom software to extract information from scientific files and transform that data into a standardized format.
Automation or analysis software also require extracting information from files. 
While the data needs of application vary, they all rely on similar algorithms to extract information from the
same types of files.
*Scythe is designed to be a shared repository for these algorithms*.

The core of Scythe is a collection of "extractors" which each generate simplified, standardized
data from a certain class of files. For example, the
:class:`~scythe.electron_microscopy.ElectronMicroscopyExtractor` produces structured data from
file types specific to brands of electron microscopes.

Each extractor does not necessarily generate data in a format needed by any tool. Rather, the extractors
are designed to produce *all* of the information needed by all projects that utilize the
libraries. In this way, the extractors can service every user without modification.

What Does Scythe *Do*?
---------------------------

Scythe is designed to provide the answer to two limited questions:

1. *Which files can I parse with a certain tool?*
    Scythe provides tools for quickly finding files of a certain type

2. *What information does a set of files contain?*
    Scythe provides a library of tools that transform data into a simpler formats

What Does Scythe *Not Do*?
-------------------------------

There are several questions that are specifically out-of-scope for Scythe:

1. *How do I get access to files that I want to parse?*
    Scythe does not solve the data transfer problem
2. *How can I parse large numbers of files reliably?*
    Scythe is not a distributed workflow engine, but is designed to integrate with one
    for extracting metadata from large filesystems.
3. *How can I translate data into the schema needed for my application?*
    The goal of Scythe is to go from opaque to well-documented formats. We recommend
    implementing separate "adapter" classes to transform Scythe metadata to your
    specific requirements.

See our
`"how to use Scythe" documentation <user-guide.html#integrating-materialsio-into-applications>`_
for more detail on how to integrate Scythe into an application that provides these
intentionally-missing features.
