"""Time utilities for AQUA diagnostics"""


def start_end_dates(startdate=None, enddate=None,
                    start_std=None, end_std=None):
    """
    Evaluate start and end dates for the reference data retrieve,
    in the case both are provided, to minimize the Reader calls.

    Args:
        startdate (datetime): start date for the data retrieve
        enddate (datetime): end date for the data retrieve
        start_std (datetime): start date for the standard deviation data retrieve
        end_std (datetime): end date for the standard deviation data retrieve

    Returns:
        tuple: start and end dates for the data retrieve
    """
    try:
        start_retrieve = min(startdate, start_std)
    except TypeError:
        start_retrieve = None

    try:
        end_retrieve = max(enddate, end_std)
    except TypeError:
        end_retrieve = None

    return start_retrieve, end_retrieve
