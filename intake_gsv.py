from gsv.retriever import GSVRetriever
import xarray as xr
from intake.source import base

class GSVSource(base.DataSource):
    container = 'xarray.Dataset'
    name = 'gsv'

    def __init__(self, request, metadata=None, **kwargs):
        self._request = request
        self._kwargs = kwargs
        self._dataset = None

    def _get_schema(self):
        if self._dataset is None:
            self._load()
        return base.Schema(
            datashape=None,
            dtype=xr.Dataset,
            shape=self._dataset.shape,
            npartitions=1,
            extra_metadata={},
        )

    def _get_partition(self, i):
        if i != 0:
            raise IndexError('partition index out of range')
        if self._dataset is None:
            self._load()
        return self._dataset

    def _load(self):
        gsv = GSVRetriever()
        self._dataset = gsv.request_data(self._request, **self._kwargs)