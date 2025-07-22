def format_realization(realization: int | str = None) -> str:
    """
    Format the realization as r<realization> if int, leave the string
    otherwise and set r1 if nothing is given.
    To be used in folder or filename creation.
    If realization is None or empty, it defaults to "r1".

    Args:
        realization (int | str, optional): the realization, either as an integer or string.
    
    Returns:
        str: the realization formatted to be used in folder or filename creation.
    """
    if realization is None or realization == "":
        return "r1"
    if isinstance(realization, int):
        return f"r{realization}"
    if isinstance(realization, str) and realization.isdigit():
        return f"r{realization}"
    return realization
