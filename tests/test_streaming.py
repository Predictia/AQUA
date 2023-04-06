import pytest
import numpy as np
import pandas as pd
from aqua import Reader, catalogue

# pytest approximation, to bear with different machines
approx_rel=1e4

# @pytest.fixture(
#     params=[
#         ("IFS", "test-tco79", "long", "r200", "2t"),
#         ("IFS", "test-tco79", "long", "r200", "ttr"),
#     ]
# )
# def reader_arguments(self, request):
#     return request.param

@pytest.fixture(scope="function")
def reader_instance():
    return Reader(model="IFS", exp="test-tco79", source="long")

# streaming class for tests
class TestAquaStreaming:

    @pytest.fixture(params=[("hours", 3), ("days", 72), ("months", 2184)])
    def stream_units(self, request):
        return request.param

    def test_stream_data_multiple(self, reader_instance, stream_units):
        """
        Test if the retrieve method returns streamed data with streaming=true with the right size
        """

        start_date = pd.to_datetime('2020-01-20T00:00:00')
        offset = pd.DateOffset(**{stream_units[0]: 3})
        step = pd.DateOffset(hours=1)

        data = reader_instance.retrieve(streaming=True, stream_step=3, stream_unit=stream_units[0])
        # Test if it has the right size
        assert data['2t'].shape == (stream_units[1], 9, 18)
        # Test if starting date is ok
        assert data.time.values[0] == start_date
        # Test if end date is ok
        assert data.time.values[-1] == start_date + offset - step

        # Test if we can go to the next date
        data = reader_instance.retrieve(streaming=True, stream_step=3, stream_unit=stream_units[0])
        assert data.time.values[0] == start_date + offset

        # Test if reset_stream works
        reader_instance.reset_stream()
        data = reader_instance.retrieve(streaming=True, stream_step=3, stream_unit=stream_units[0])
        assert data.time.values[0] == start_date


# self.stream_index = data.time.to_index().get_loc(pd.to_datetime(stream_startdate))

#         if stream_unit:
#             start_date = self.stream_date
#             stop_date = start_date + pd.DateOffset(**{stream_unit: stream_step})
#             self.stream_date = stop_date


    # def test_regrid_data(self, reader_instance):
    #     """
    #     Test if the regrid method returns data with the expected shape and values
    #     """
    #     data = reader_instance.retrieve(fix=False)
    #     sstr = reader_instance.regrid(data["sst"][0:2, :])
    #     assert sstr.shape == (2, 90, 180)
    #     assert np.nanmean(sstr[0, :, :].values) == pytest.approx(13.350324258783935, rel=approx_rel)
    #     assert np.nanmean(sstr[1, :, :].values) == pytest.approx(13.319154700343551, rel=approx_rel)

    # def test_fldmean(self, reader_instance):
    #     """
    #     Test if the fldmean method returns data with the expected shape and values
    #     """
    #     data = reader_instance.retrieve(fix=False)
    #     global_mean = reader_instance.fldmean(data.sst[:2, :])
    #     assert global_mean.shape == (2,)
    #     assert global_mean.values[0] == pytest.approx(17.99434183, rel=approx_rel)
    #     assert global_mean.values[1] == pytest.approx(17.98060367, rel=approx_rel)

    # @pytest.fixture(
    #     params=[
    #         ("IFS", "test-tco79", "short", "r200", "tas"),
    #         ("FESOM", "test-pi", "original_2d", "r200", "sst"),
    #     ]
    # )
    # def reader_arguments(self, request):
    #     return request.param

    # def test_reader_with_different_arguments(self, reader_arguments):
    #     """
    #     Test if the Reader class works with different combinations of arguments
    #     """
    #     model, exp, source, regrid, variable = reader_arguments
    #     reader = Reader(model=model, exp=exp, source=source, regrid=regrid)
    #     data = reader.retrieve(fix=False)
    #     assert len(data) > 0
