"""
Module including string utilities for AQUA
"""

def strlist_to_phrase(items: list[str], oxford_comma: bool = False) -> str:
    """
    Convert a list of str to a english-consistent list.
       ['A'] will return "A"
       ['A','B'] will return "A and B"
       ['A','B','C'] will return "A, B and C" (oxford_comma=False)
       ['A','B','C'] will return "A, B, and C" (oxford_comma=True)
       
    Args:
        items (list[str]): The list of strings to format.
    """
    if not items: return ""
    if len(items) == 1: return items[0]
    if len(items) == 2: return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + (", and " if oxford_comma else " and ") + items[-1]


def lat_to_phrase(lat: int) -> str:
    """
    Convert a latitude value into a string representation.

    Returns:
        str: formatted as "<deg>°N" for northern latitudes or "<deg>°S" for southern latitudes.
    """
    if lat >= 0:
        return f"{lat}°N"
    if lat < 0:
        return f"{abs(lat)}°S"