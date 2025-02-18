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
    start_retrieve = min(filter(None, [startdate, start_std])) if any([startdate, start_std]) else None
    end_retrieve = max(filter(None, [enddate, end_std])) if any([enddate, end_std]) else None

    return start_retrieve, end_retrieve
