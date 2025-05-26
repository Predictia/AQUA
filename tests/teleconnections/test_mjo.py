import os
import matplotlib
import pytest
from aqua.diagnostics.teleconnections import ENSO, PlotENSO

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.diagnostics
def test_MJO(tmp_path):
    """
    Test that the MJO class works
    """