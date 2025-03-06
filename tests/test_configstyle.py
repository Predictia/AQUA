import os
import matplotlib.pyplot as plt
import pytest
from aqua.graphics import ConfigStyle

@pytest.mark.configstyle
def test_ConfigStyle():
    """
    Test that ConfigStyle class is correctly initialized
    """
    style = 'aqua.mplstyle'

    cs = ConfigStyle(style=style)
    assert cs.style == style