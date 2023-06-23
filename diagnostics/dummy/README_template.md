# Dummy diagnostic

This is a dummy diagnostic that does nothing.
It is meant to be used as a template for new diagnostics.

## Description

Concise overview that explains the purpose, key features, and benefits of your diagnostics.

## Table of Contents

* [Installation Instructions](#installation-instructions)

  - [Installation on Levante](#installation-on-levante)

  - [Installation on Lumi](#installation-on-lumi)

* [Diagnostic structure](#diagnostic-structure)

* [Code](#code)

* [Data requirements](#data-requirements)

* [Examples](#examples)


* [Contributing](#contributing)

## Installation Instructions

Clearly explain how to install and set up your project. Include any dependencies, system requirements, or environment configurations that users should be aware of.

### Installation on Levante


### Installation on Lumi 

## Diagnostic structure 

- **diagnostics/**: The root directory of the diagnostic.

  - **dummy/**: contains the code of the diagnostic

    - **notebooks/**: contains notebooks with examples of how to use the diagnostic

    - **data/**: contains data for the tests (if needed). 

    - **env-dummy.yml**: contains the dependencies for the diagnostic. 

- **tests/**

  - **dummy/**: contains tests for the diagnostic.  The tests of the diagnostic have a marker `@pytest.mark.yourdiag`. 



- **docs/sphinx/sorce/diagnostics/dummy.rts**: contains the documentation for the dummy diagnostic. 

## Code

Provide a brief description of your code.

## Data requirements  

Please specify if your diagnostic can only be performed on data with particular requirements. If your diagnostics have no Data requirements, you should also document that.

## Examples

The **notebook/** folder contains the following notebooks:

- **dummy.ipynb**: 
  Provide a brief description for each notebook (2-3 sentences).
- 

## Contributing

Include your contact information or any official channels (such as email, GitHub profile) through which users can reach out to you for support, questions, or feedback.

