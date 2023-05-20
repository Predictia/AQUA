"""Common functions for the Reader"""
import xarray as xr


def check_catalog_source(cat, model, exp, source, name="dictionary"):
    """
    Check the entries of a nested dictionary based on the model/exp/source structure
    and return an updated source. The name argument can be used for proper printing.

    Args:
        cat (dict): The nested dictionary containing the catalog information.
        model (str): The model ID to check in the catalog.
        exp (str): The experiment ID to check in the catalog.
        source (str): The source ID to check in the catalog.
        name (str, optional): The name used for printing. Defaults to "dictionary".

    Returns:
        str: An updated source ID. If the source is not specified, "default"
            is chosen, or, if missing, the first source.
    """

    if model not in cat:
        raise KeyError(f"Model {model} not found in {name}.")
    if exp not in cat[model]:
        raise KeyError(f"Experiment {exp} not found in {name} for model {model}.")
    if not cat[model][exp].keys():
        raise KeyError(f"Experiment {exp} in {name} for model {model} has no sources")

    if source:
        if source not in cat[model][exp]:
            if "default" not in cat[model][exp]:
                raise KeyError(f"Source {source} of experiment {exp} "
                               f"not found in {name} for model {model}.")
            source = "default"
    else:
        source = list(cat[model][exp].keys())[0]  # take first source if none provided

    return source


def group_shared_dims(ds, shared_dims, others=None):
    """
    Groups variables in a dataset that share the same dimension.

    Arguments:
        ds (xarray.Dataset or xarray.DataArray): Input dataset or dataarray to group variables
        shared_dims (list): List of shared dimensions
        others (str, optional): Name of group for variables not in `shared_dims`.
                                Not computed if not specified.

    Returns:
        Dictionary containing datasets that share the same dimension
    """

    # Is this a DataArray?
    if not isinstance(ds, xr.Dataset):
        dim = [x for x in shared_dims if x in ds.dims]
        if dim:
            return {dim[0]: ds}
        else:
            if others:
                return {others: ds}
            else:
                raise ValueError("No shared dimensions found.")

    shared_vars = {}
    for dim in shared_dims:
        vlist = []
        for var in ds.data_vars:
            if dim in ds[var].dims:
                vlist.append(var)
        shared_vars.update({dim: ds[vlist]})
    if others:
        vlist = []
        for var in ds.data_vars:
            if not any(x in shared_dims for x in ds[var].dims):
                vlist.append(var)
        if vlist:
            shared_vars.update({others: ds[vlist]})

    return shared_vars
