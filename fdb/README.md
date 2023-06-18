# AQUA FDB

This directory contains an example FDB repository configured
for testing the access to FDB with AQUA.

These files are bound as a volume to a Docker container. Or
developers can use these files directly on their environments
for running tests or notebooks.

## Test data

The current test data `sample_test_data.grib` is a single GRIB1
file downloaded from CDS using the Python API.

## FDB configuration

In this directory you should find a `config.yaml` file. This
was crafted for the test data used, and may not work with other
data.

The `config.yaml` file points to folders used by default in the
container.

Another file that must be present is the `schema`. This is perhaps
the most important file. It tells FDB what is the schema of the
repository.

When you request data (`fdb-read`, `fdb-list`, etc.) FDB verifies
that the request is valid for the schema, and in case it is, then
it fetches to TOC and Index and loads the requested data and writes
it all in the user stream.

The `schema` file is also consulted when writing data into an FDB.

## Container setup

The FDB container, by default, uses the /app/ directory to hold
`config.yaml` and `schema`, and the data is stored under the
`/app/localroot` directory.

In the GitHub Actions definition we delete the `/app` and replace
it by a copy of the `./fdb` directory. In other words, this very
directory will be `/app/` inside the container.

Then, `fdb-write sample_test_data.grib` is executed when the
container is initialized in GitHub actions.

This sets up the GitHub Actions for any test that requires
an FDB, like the tests that use the GSV Interface.

Note, however, that there are other variables that must also be
defined in order for GSV to use the correct FDB, namely:

- `FDB5_CONFIG_FILE=/app/config.yaml`
- `LD_LIBRARY_PATH=/opt/eccodes/lib:/opt/eckit/lib/:/opt/metkit/lib/:/opt/fdb/lib/`
- `GRID_DEFINITION_PATH=/tmp`

The two first variables are set by default in the container, but
users that have installed FDB (and ecCodes, MetKit, ecKit, etc.)
locally will have to adjust these values.

The last variable is used only when you have to use other grids
in GSV when loading data. The current tests in AQUA do not use
this feature, but it is important to set this value. This is
done in GitHub Actions for the container (do it in your local
environment if running the tests locally.)
