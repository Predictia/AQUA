def retrieve_merge_ensemble_data(
    variable: str = None,
    region: str = None,
    ens_dim: str = "ensemble",
    data_path_list: list[str] = None,
    models_catalog_list: list[str] = None,
    exps_catalog_list: list[str] = None,
    sources_catalog_list: list[str] = None,
    startdate: str = None,
    enddate: str = None,
    log_level: str = "WARNING",
):
    """
    Retrieves, merges, and slices datasets based on specified models, experiments,
    sources, and time boundaries.

    This function reads data for a given variable (`variable`) from multiple models, experiments,
    and sources, combines the datasets along the specified "ensemble" dimension along with their indices, and slices
    the merged dataset to the given start and end dates. The ens_dim can given any customized name for the ensemble dimension.

    There are following two ways to load the datasets with function.
    a) with xarray.open_dataset
    b) with AQUA Reader class

    Args:
        variable (str): The variable to retrieve data. Defaults to None.
        In the case a):
            data_path_list (list of str): list of paths for data to be loaded by xarray.
        In the case b):
            region (str): This variable is specific to the Zonal averages. Defaults to None.
            models_catalog_list (list): A list of model names. Each model corresponds to an
                experiment and source in the `exps` and `sources` lists, respectively.
                Defaults to None.
            exps_catalog_list (list): A list of experiment names. Each experiment corresponds
                to a model and source in the `models` and `sources` lists, respectively.
                Defaults to None.
            sources_catalog_list (list): A list of data source names. Each source corresponds
                to a model and experiment in the `models` and `exps` lists, respectively.
                Defaults to None.

        Specific to the timeseries datasets:
            startdate (str or datetime): The start date for slicing the merged dataset.
                If None is provided, the ensemble members are merged w.r.t to their time-interval. Defaults to None.
            enddate (str or datetime): The end date for slicing the merged dataset.
                If None is provided, the ensemble members are merged w.r.t to their time-interval. Defaults to None.
    Returns:
            In case of timeseries dataset:
                - common_startdate (datetime): Outputs a common start date for the merged dataset.
                - common_enddate (datetime): Outputs a common end date for the merged dataset.
                - xarray.Dataset: The merged dataset containing data from all specified models,
                experiments, and sources, concatenated along `ens_dim`
            Otherwise:
                - xarray.Dataset for the given dataset.
    """
    logger = log_configure(log_name="retrieve_merge_ensemble_data", log_level=log_level)
    logger.info("Loading and merging the ensemble dataset")

    # in case if the list of paths of netcdf dataset is given
    # then load via xarray.open_dataset function
    # return ensemble dataset with ensemble dimension name as 'ensemble' with individual indexes
    if data_path_list is not None:
        ens_dataset = xr.concat(
            [
                xr.open_dataset(
                    f,
                    drop_variables=[var for var in xr.open_dataset(f).variables if var != variable],
                ).expand_dims({ens_dim: [i]})
                for i, f in enumerate(data_path_list)
            ],
            dim=ens_dim,
        )
    # else if check the models, exps and sources are given from the catalog in the forms of lists
    # then use the AQUA.Reader class to load the data
    elif (
        models_catalog_list is not None
        and exps_catalog_list is not None
        and sources_catalog_list is not None
    ):
        tmp_dataset_list = []
        for i, model in enumerate(models_catalog_list):
            if region is not None:
                tmp_reader = Reader(
                    model=model,
                    exp=exps_catalog_list[i],
                    source=source_catalog_list[i],
                    areas=False,
                    region=region,
                )
            else:
                tmp_reader = Reader(
                    model=model,
                    exp=exps_catalog_list[i],
                    source=source_catalog_list[i],
                    areas=False,
                    region=region,
                )
            # tmp_dataset = tmp_reader.retrieve(var=variable)
            tmp_dataset = tmp_reader.retrieve(var=variable)
            tmp_dataset_expended = tmp_dataset.expand_dims(ensemble=[i])
            tmp_dataset_list.append(tmp_dataset_expended)
        # concatenate along the ensemble dimension
        ens_dataset = xr.concat(tmp_dataset_list, dim="ensemble")
        # delete all tmp varaibles
        del tmp_dataset_list, tmp_reader, tmp_dataset, tmp_dataset_expended
        gc.collect()
    else:
        raise NoDataError("No Data is provided to retreieve and merge for ensemble")
    # check if the ensemble dataset is a timeseries dataset
    # then return enemble dataset and also output the common time-interval
    if "time" in ens_dataset.dims:
        if startdate is None:
            common_startdate = max(times[0] for times in (pd.to_datetime(ds.sel({ens_dim: member})['time'].values) for member in ds[ens_dim]))
            #startdate = ens_dataset.time.min(dim="time")
        if enddate is None:
            common_enddate = min(times[-1] for times in (pd.to_datetime(ds.sel({ens_dim: member})['time'].values) for member in ds[ens_dim]))
            #enddate = ens_dataset.time.max(dim="time")
        logger.info("Finished loading the ensemble timeseries datasets")
        return ens_dataset, common_startdate, common_enddate
    else:
        # the ensemble dataset is not a timeseries
        logger.info("Finished loading the ensemble datasets")
        return ens_dataset
