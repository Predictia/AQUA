Installation
============

Prerequisites
-------------

Before installing AQUA, ensure that you have the following software installed on your system:

- Python 3.7 or higher
- pip (Python package installer)

You may also want to use a virtual environment to isolate the package installation. This can be done using tools like `virtualenv` or `conda`.

Installing AQUA
---------------

To install the latest stable version of AQUA, open a terminal or command prompt and run the following command:

.. code-block:: bash

   pip install AQUA

If you want to install the development version of AQUA, you can clone the repository from GitHub and install it using pip:

.. code-block:: bash

   git clone https://github.com/your-organization/AQUA.git
   cd AQUA
   pip install .

Optional Dependencies
---------------------

Some features in AQUA may require additional packages to function properly. These optional dependencies can be installed alongside AQUA using the following command:

.. code-block:: bash

   pip install AQUA[optional]

Replace "optional" with the specific feature name or group of features you want to install. For example, if you want to install dependencies for advanced visualization, you might use:

.. code-block:: bash

   pip install AQUA[visualization]

Consult the AQUA documentation for a complete list of optional dependencies and their corresponding feature names.
