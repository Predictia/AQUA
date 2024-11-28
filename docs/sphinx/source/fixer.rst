.. _fixer:

Fixer functionalities
---------------------

The need of comparing different datasets or observations is very common when evaluating climate models.
However, datasets may have different conventions, units, and even different names for the same variable.
AQUA provides a fixer tool to standardize the data and make them comparable.

The general idea is to convert data from different models to a uniform file format
with the same variable names and units.
The default convention for metadata (for example variable ShortNames) is **GRIB**.

The fixing is done by default when we initialize the ``Reader`` class, 
using the instructions in the ``config/fixes`` folder.

The ``config/fixes`` folder contains fixes in YAML files.
A new fix can be added to the folder and the filename can be freely chosen.
By default, fixes files with the name of the model or the name of the DestinE project are provided.

If you need to develop your own, fixes can be specified in two different ways:

- Using the ``fixer_name`` definitions, to be then provided as a metadata in the catalog source entry.
  This represents fixes that have a common nickname which can be used in multiple sources when defining the catalog.
  There is the possibility of specifing a **parent** fix so that a fix can be re-used with minor corrections,
  merging small changes to a larger ``fixer_name``.
- Using the source-based definition.
  Each source can have its own specific fixes.
  These are used only if a ``fixer_name`` is not specified for the source.

.. warning::  
    Please note that the source-based definition is the older AQUA implementation and will be deprecated
    in favour of the new approach described above.
    We strongly suggest to use the new approach for new fixes.

.. note::
    If no ``fixer_name`` is provided and ``fix`` is set to ``True``, the code will look for a
    ``fixer_name`` called ``<MODEL_NAME>-default``.

Please note that the ``default.yaml`` is reserved to define a few of useful tools:

- the default ``data_model`` (See :ref:`coord-fix`).
- the list of units that should be added to the default MetPy unit list. 
- A series of nicknames (``shortname``) for units to be replaced in the fixes yaml file.

Concept
^^^^^^^

The fixer performs a range of operations on data:

- adopts a **common data model** for coordinates (default is the CDS common data model):
  names of coordinates and dimensions (lon, lat, etc.),
  coordinate units and direction, name (and meaning) of the time dimension. (See :ref:`coord-fix` for more details)
- changes variable names deriving the correct metadata from GRIB tables if required.
  The fixer can identify these derived variables by their ShortNames and ParamID (ECMWF and WMO eccodes tables are used).
- derives new variables executing trivial operations as multiplication, addition, etc. (See :ref:`metadata-fix` for more details)
  In particular, it derives from accumulated variables like ``tp`` (in mm), the equivalent mean-rate variables
  (like ``mtpr`` in kg m-2 s-1). (See :ref:`metadata-fix` for more details)
- using the ``metpy.units`` module, it is capable of guessing some basic conversions.
  In particular, if a density is missing, it will assume that it is the density of water and will take it into account.
  If there is an extra time unit, it will assume that division by the timestep is needed. 

.. _fix-structure:

Fix structure
^^^^^^^^^^^^^

Here we show an example of a fixer file, including all the possible options:

.. code-block:: yaml

    fixer_name:
        documentation-mother: 
            data_model: ifs
            delete: 
                - bad_variable
            vars:
                mtpr:
                    source: tp
                    grib: true
        documentation-fix:
            parent: documentation-to-merge
            data_model: ifs
            dims:
                cells:
                    source: cells-to-rename
            coords:
                time:
                    source: time-to-rename
            deltat: 3600 # Decumulation info
            jump: month
            vars:
                2t:
                    source: 2t
                    attributes: # new attribute
                        donald: 'duck'
                mtntrf: # Auto unit conversion from eccodes
                    derived: ttr
                    grib: true
                    decumulate: true     
                2t_increased: # Simple formula
                    derived: 2t+1.0
                    grib: true
                # example of derived variable, should be double the normal amount
                mtntrf2:
                    derived: ttr+ttr
                    src_units: J m-2 # Overruling source units
                    decumulate: true  # Test decumulation
                    units: "{radiation_flux}" # overruling units
                    mindate: 1990-09-01T00:00 # setting to NaN all data before this date
                    attributes:
                        # assigning a long_name
                        long_name: Mean top net thermal radiation flux doubled
                        paramId: '999179' # assigning an (invented) paramId

We put together many different fixes, but let's take a look at the 
different sections of the fixer file.

- **documentation-fix**: This is the name of the fixer.
    It is used to identify the fixer and will be used in the entry metadata
    to specify which fixer to use. (See :ref:`add-data` for more details)
- **parent**: a source ``fixer_name`` with which the current fixes have to be merged. 
    In the above example, the ``documentation-fix`` will extend the ``documentation-mother`` fix integrating it. 
- **data_model**: the name of the data model for coordinates. (See :ref:`coord-fix`).
- **coords**: extra coordinates handling if data model is not flexible enough.
    (See :ref:`coord-fix`).
- **dims**: extra dimensions handling if data model is not flexible enough. 
    (See :ref:`coord-fix`).
- **decumulation**: 
    - If only ``deltat`` is specified, all the variables that are considered as cumulated flux variables 
      (i.e. that present a time unit mismatch from the source to target units) will be divided
      by ``deltat``. This is done automatically based on the values of target and source units.
      ``deltat`` can be an integer in seconds, or alternatively a string with `monthly`: in this case
      each flux variable will be divided by the number of seconds of each month.
    - If additionally ``decumulate: true`` is specified for a specific variable,
      a time derivative of the variable will be computed.
      This is tipically done for cumulated fluxes for the IFS model, that are cumulated on a period longer
      than the output saving frequency.
      The additional ``jump`` parameter specifies the period of cumulation.
      Only months are supported at the moment, implying that fluxes are reset at the beginning of each month.
- **timeshift**: Roll the time axis forward/back in time by a certain amount. This could be an integer that will
    be interpreted as a number of timesteps, or a pandas Timedelta string (e.g. `1D`). Positive numbers
    will move the time axis forward, while negative ones will move it backward (e.g. `-2H`). Please note that only the 
    time axis will be affected, the Dataset will maintain all its properties. 
- **vars**: this is the main fixer block, described in detail on the following section :ref:`metadata-fix`.
- **delete**: a list of variable or coordinates that the users want to remove from the output Dataset

.. _metadata-fix:

Metadata Correction
^^^^^^^^^^^^^^^^^^^^

The **vars** block in the ``fixer_name`` represent a list of variables that need
metadata correction: this covers units, names, grib codes, and any other metadata.
In addition, also new variables can be computed from pre-existing variables.

The above-reported section :ref:`fix-structure` provides an exhaustive list of cases. 
In order to create a fix for a specific variable, two approaches are possibile:

- **source**: it will modify an existent variable changing its name (e.g from ``tp`` to ``mtpr``)
- **derived**: it will create a new variable, which can also be obtained with basic operations between
  multiple variables (e.g. getting ``mtntrf2`` from ``ttr`` + ``tsr``). 

.. warning ::
    Please note that only basic operation (sum, division, subtraction and multiplication) are allowed in the ``derived`` block

Then, extra keys can be then specified for `each` variable to allow for further fine tuning:

- **grib**: if set ``True``, the fixer will look for GRIB ShortName associated with the new variable and 
  will retrieve the associated metadata.
- **src_units**: override the source unit in case of specific issues (e.g. units which cannot be processed by MetPy).
- **units**: override the target unit.
- **decumulate**: if set to ``True``, activate the decumulation of the variables
- **attributes**: with this key, it is possible to define a dictionary of attributes to be modified. 
  Please refer to the above example to see the possible implementation. 
- **mindate**: used to set to NaN all data before a specified date. 
  This is useful when dealing with data that are not available for the whole period of interest or which are partially wrong.

.. warning ::
    Recursive fixes (i.e. fixes of fixes) cannot be implemented. For example, it is not possibile to derive a variable from a derived variable

.. _coord-fix:

Data Model and Coordinates/Dimensions Correction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The fixer can adopt a common *coordinate data model*
(default is the CDS data model).
If this data model is not appropriate for a specific source,
it is possible to specify a different one in the catalog source.

If the data model coordinate treatment is not enough to fix the coordinates or dimensions,
it is possible to specify a custom fix in the catalog in the **coords** or **dims** blocks
as shown in section :ref:`fix-structure`.
For example, if the longitude coordinate is called ``longitude`` instead of ``lon``,
it is possible to specify a fix like:

.. code-block:: yaml

    coords: 
        lon:
            source: longitude

This will rename the coordinate to ``lon``.

.. note::
    When possible, prefer a **data model** treatment of coordinates and use the **coords**
    block as second option.

Similarly, if units are ill-defined in the dataset, it is possible to override them with the same fixer structure. 
Of course, this feature is valid only for **coords**:

.. code-block:: yaml

    coords: 
        level:
            tgt_units: m

.. warning::
    Please keep in mind that coordinate units is simply an override of the attribute. It won't make any assumption on the source units and will not convert it accordingly.