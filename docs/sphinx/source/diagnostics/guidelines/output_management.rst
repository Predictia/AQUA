Automatic Standardized File Naming
==================================

Class Overview
--------------

The ``OutputSaver`` class is designed to manage output file naming conventions for scientific data.
It supports generating filenames for various types of file (e.g., NetCDF, PDF, PNG) with metadata integration to enhance data management and traceability.
The class ensures consistent and descriptive filenames, facilitating better data management and reproducibility.

Attributes
----------

- **diagnostic** (*str*): Name of the diagnostic.
- **model** (*str*): Model used in the diagnostic.
- **exp** (*str*): Experiment identifier.
- **diagnostic_product** (*str, optional*): Product of the diagnostic analysis.
- **loglevel** (*str, optional*): Log level for the class's logger. Default is 'WARNING'.
- **default_path** (*str, optional*): Default path where files will be saved. Default is '.'.
- **rebuild** (*bool, optional*): Flag indicating whether to rebuild existing files. If set to True, existing files with the same name will be overwritten. Default is True.

.. note::
    The ``OutputSaver`` class automatically includes the current date and time when saving files as metadata ``date_saved``.
    This ensures each file has a timestamp indicating when it was generated.

Usage Examples
--------------

Initializing the OutputSaver Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following example demonstrates how to initialize the ``OutputSaver`` class:

.. code-block:: python

    from aqua.util import OutputSaver

    names = OutputSaver(diagnostic='tropical_rainfall', model='MSWEP', exp='past',
                        loglevel='debug', default_path='.')

Generating a Filename for a NetCDF File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example shows how to generate a filename for a NetCDF file with the 'mean' diagnostic product for the previously initialized class.
This and the following methods return the generated filename as a string, to be used with the incorporated methods or with other functions.

.. code-block:: python

    netcdf_filename = names.generate_name(diagnostic_product='mean', suffix='nc')

Generating a Filename with Flexible Date Inputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates generating a filename with flexible date inputs and the 'ym' time precision:

.. code-block:: python

    filename = names.generate_name(var='mtpr', model_2='ERA5', exp_2='era5',
                                   time_start='1990-01', time_end='1990-02',
                                   time_precision='ym', area='indian_ocean')

Saving a NetCDF File with Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here is an example of saving a NetCDF file with metadata. The metadata includes the title, author, and description of the file.

.. code-block:: python

    import xarray as xr

    # Example dataset
    dataset = xr.Dataset()

    # Define metadata for the NetCDF file
    metadata = {
        'title': 'Testing the saving of NetCDF files',
        'author': 'OutputSaver',
        'description': 'Demonstrating netCDF Metadata Addition'
    }

    # Save the NetCDF to the specified path with the metadata
    saved_file_path = names.save_netcdf(dataset, path='.', diagnostic_product='histogram',
                                        metadata=metadata)

.. note::

    If the ``history`` metadata field is provided, the ``OutputSaver`` class will append
    the current message to the existing history.

Saving a PDF Plot with Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates saving a PDF plot with metadata. The metadata includes the title, author, subject, and keywords of the PDF.

.. code-block:: python

    import matplotlib.pyplot as plt

    # Create a sample figure
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])

    # Define metadata for the PDF file
    metadata = {
        '/Title': 'Sample PDF',
        '/Author': 'OutputSaver',
        '/Subject': 'Demonstrating PDF Metadata Addition',
        '/Keywords': 'PDF, OutputSaver, Metadata'
    }

    # Save the PDF with metadata
    pdf_path = names.save_pdf(fig, diagnostic_product='histogram', metadata=metadata, dpi=300)

.. note::

    We suggest at the moment to use the metadata ``/Caption`` field to store the plot description.
    This is used at the moment by the AQUA dashboard to generate the plot description.

Opening a PDF File and Displaying Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To open a PDF file and display its metadata:

.. code-block:: python

    from aqua.util import open_image

    open_image("/path/to/my/file/tropical_rainfall.histogram.IFS-NEMO.historical-1990.pdf")
