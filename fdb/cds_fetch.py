#!/usr/bin/env python
# https://cds.climate.copernicus.eu/api-how-to

"""Simple script used to retrieve the test data."""

import cdsapi

c = cdsapi.Client()
c.retrieve("reanalysis-era5-pressure-levels",
           {
               "variable": "temperature",
               "pressure_level": "1000",
               "product_type": "reanalysis",
               "year": "2008",
               "month": "01",
               "day": "01",
               "time": "12:00",
               "format": "grib",
               "expver": "0001",
               "class": "rd",
               "stream": "oper"
           }, "sample_test_data.grib")

# The file is GRIB1, but that does not matter (or you can
# ``grib_set -s edition=2 download.grib download.grib2`).
