OutputNamer Class Documentation
===============================

Class Overview
--------------

The `OutputNamer` class is designed to manage output file naming conventions for scientific data. It supports generating filenames for various types of files (e.g., NetCDF, PDF, PNG) with metadata integration to enhance data management and traceability. The class ensures consistent and descriptive file names, facilitating better data management and reproducibility.

Attributes
----------

- **diagnostic** (*str*): Name of the diagnostic.
- **model** (*str*): Model used in the diagnostic.
- **exp** (*str*): Experiment identifier.
- **diagnostic_product** (*str, optional*): Product of the diagnostic analysis.
- **loglevel** (*str, optional*): Log level for the class's logger. Default is 'WARNING'.
- **default_path** (*str, optional*): Default path where files will be saved. Default is '.'.
- **rebuild** (*bool, optional*): Flag indicating whether to rebuild existing files. If set to True, existing files with the same name will be overwritten. Default is True.

Key Metadata
------------

The `OutputNamer` class automatically includes the current date and time when saving files as metadata (`date_saved`). This ensures each file has a timestamp indicating when it was generated.

Usage Examples
--------------

Initializing the OutputNamer Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following example demonstrates how to initialize the `OutputNamer` class:

.. code-block:: python

    from aqua.util import OutputNamer

    # Initialize the OutputNamer class instance
    names = OutputNamer(diagnostic='tropical_rainfall', model='MSWEP', exp='past', loglevel='debug', default_path='.')

Generating a Filename for a NetCDF File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example shows how to generate a filename for a NetCDF file with the 'mean' diagnostic product:

.. code-block:: python

    # Generate a filename for a NetCDF file with the 'mean' diagnostic product
    netcdf_filename = names.generate_name(diagnostic_product='mean', suffix='nc')
    print(netcdf_filename)

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
        'author': 'OutputNamer',
        'description': 'Demonstrating netCDF Metadata Addition'
    }

    # Save the NetCDF to the specified path with the metadata
    saved_file_path = names.save_netcdf(dataset, path='.', diagnostic_product='histogram', metadata=metadata)
    print(f"netCDF with metadata saved to: {saved_file_path}")

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
        '/Author': 'OutputNamer',
        '/Subject': 'Demonstrating PDF Metadata Addition',
        '/Keywords': 'PDF, OutputNamer, Metadata'
    }

    # Save the PDF with metadata
    pdf_path = names.save_pdf(fig, diagnostic_product='histogram', metadata=metadata, dpi=300)
    print(f"PDF saved to: {pdf_path}")

Opening a PDF File and Displaying Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To open a PDF file and display its metadata:

.. code-block:: python

    from aqua.util import open_image

    # Provide a link to the saved PDF file
    open_image("/users/nazarova/work/demo/netcdf/output_test/tropical_rainfall.histogram.IFS-NEMO.historical-1990.pdf")

Warning
-------

By default, the `OutputNamer` class will always include a `date_saved` metadata field, recording the date and time the file was saved. This ensures traceability and reproducibility of the generated files.