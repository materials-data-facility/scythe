# Scythe

[![Build Status](https://github.com/materials-data-facility/Scythe/workflows/Build%20Status/badge.svg)](https://github.com/materials-data-facility/Scythe/actions/workflows/test-suite-and-docs.yml)
[![Documentation](https://img.shields.io/badge/-Documentation-blue?style=flat&logo=bookstack&labelColor=grey&logoColor=white)](https://materials-data-facility.github.io/Scythe)
[![Coverage Status](https://codecov.io/gh/materials-data-facility/Scythe/branch/master/graph/badge.svg)](https://codecov.io/gh/materials-data-facility/Scythe)
[![GitHub last commit](https://img.shields.io/github/last-commit/materials-data-facility/Scythe)](https://github.com/materials-data-facility/Scythe/commits/master)
[![PyPI version](https://badge.fury.io/py/scythe-extractors.svg)](https://badge.fury.io/py/scythe-extractors)
[![GitHub contributors](https://img.shields.io/github/contributors/materials-data-facility/Scythe)](https://github.com/materials-data-facility/Scythe/graphs/contributors)

Scythe is a library of tools that generate summaries of the data contained in scientific data files.
The goal of Scythe is to provide a shared resources of these tools ("extractors") to avoid duplication of effort between the many emerging materials databases.
Each extractor is designed to generate the sum of all data needed by each of these databases with a uniform API so that specific projects can write simple adaptors for their needs.

## Installation

Install using an up-to-date version of `pip` on version 3.8 or higher of Python:

```bash
pip install scythe-extractors
```

Each specific extractor module has its own set of required libraries.
Given that some modules have extensive dependencies, we do not install all of them automatically.
You can install them either module-by-module using the pip "extras" installation (e.g., 
`pip install scythe-extractors[image]"`),
or install all extractors with 
`pip install scythe-extractors[all]"`.

## Development/Contribution

If you wish to develop new features using Scythe, please consult the 
[Contributor Guide](https://materialsio.readthedocs.io/en/latest/contributor-guide.html) that will
walk you through installing [Poetry](https://python-poetry.org/) and the Scythe dependencies.

## Documentation

* Complete documentation for Scythe is on [Read the Docs](https://materialsio.readthedocs.io/en/latest/).
* [List of Available Extractors](https://materialsio.readthedocs.io/en/latest/extractors.html)

## Support 

This work was performed in partnership with [Citrine Informatics](https://citrine.io/). 
This was also performed under financial assistance award 70NANB14H012 from U.S. Department of Commerce, National Institute of Standards and Technology as part of the Center for Hierarchical Material Design (CHiMaD).
This work was also supported by the National Science Foundation as part of the Midwest Big Data Hub under NSF Award Number: 1636950 "BD Spokes: SPOKE: MIDWEST: Collaborative: Integrative Materials Design (IMaD): Leverage, Innovate, and Disseminate".
