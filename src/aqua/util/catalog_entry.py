from .config import ConfigPath

def replace_intake_vars(path: str, catalog: str | None = None) -> str:
    """
    Replace the intake jinja vars into a string for a predefined catalog

    Args:
        path: the original path that you want to update with the intake variables
        catalog:  the catalog name where the intake vars must be read

    Returns:
        The updated path with the intake variables replaced.
    """

    # We exploit of configurerto get info on intake_vars so that we can replace them in the urlpath
    Configurer = ConfigPath(catalog=catalog)
    _, intake_vars = Configurer.get_machine_info()
    
    # loop on available intake_vars, replace them in the urlpath
    for name in intake_vars.keys():
        replacepath = intake_vars[name]
        if replacepath is not None and replacepath in path:
            # quotes used to ensure that then you can read the source
            path = path.replace(replacepath, "{{ " + name + " }}")

    return path