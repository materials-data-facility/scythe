# MaterialsIO

[![Build Status](https://travis-ci.org/materials-data-facility/MaterialsIO.svg?branch=master)](https://travis-ci.org/materials-data-facility/MaterialsIO)

MaterialsIO is a library of tools that generate summaries of the data contained in scientific data files.
The goal of MaterialsIO is to provide a shared resources of these tool to avoid duplication of effort between the many emerging materials databases.
Each parser is designed to generate the sum of all data needed by each of these databases with a uniform API so that specific projects can write simple adaptors for their needs.

## Installation

MaterialsIO is still under early stages of development. 
To use it, first clone this repository and then install the library with pip:

```bash
git clone git@github.com:materials-data-facility/MaterialsIO.git
cd MaterialsIO
pip install -e .
```  

## Support 

This work was performed in partnership with [Citrine Informatics](https://citrine.io/). 
This was also performed under financial assistance award 70NANB14H012 from U.S. Department of Commerce, National Institute of Standards and Technology as part of the Center for Hierarchical Material Design (CHiMaD).
This work was also supported by the National Science Foundation as part of the Midwest Big Data Hub under NSF Award Number: 1636950 "BD Spokes: SPOKE: MIDWEST: Collaborative: Integrative Materials Design (IMaD): Leverage, Innovate, and Disseminate".
