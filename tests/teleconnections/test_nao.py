import pytest

# pytest approximation, to bear with different machines
approx_rel = 1e-4
loglevel = 'DEBUG'

@pytest.mark.teleconnections
def test_class_NAO():
    """
    Test that the NAO class works
    """
    from teleconnections import Teleconnection

    telecname = 'NAO'
    model = 'IFS'
    exp = 'r1i1p1f1'
    source = 'monthly'

    telec = Teleconnection(model=model, exp=exp, source=source,
                           loglevel=loglevel, telecname=telecname)

    telec.evaluate_index()
    assert telec.index is not None

    telec.evaluate_regression()
    assert telec.regression is not None

    telec.evaluate_correlation()
    assert telec.correlation is not None

    # asser some values for each of the above
