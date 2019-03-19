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
