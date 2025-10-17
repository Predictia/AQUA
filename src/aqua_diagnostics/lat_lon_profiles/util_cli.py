"""Utility functions for the LatLonProfiles CLI."""

def load_var_config(config_dict, var, diagnostic='lat_lon_profiles'):
    """Load variable configuration from config dictionary.
    
    Args:
        config_dict (dict): Configuration dictionary.
        var (str or dict): Variable name or variable configuration dictionary.
        diagnostic (str): Diagnostic name.

    Returns:
        tuple: Variable configuration dictionary and list of regions.
    """
    if isinstance(var, dict):
        var_name = var.get('name')
        var_config = var
    else:
        var_name = var
        var_config = config_dict['diagnostics'][diagnostic].get('params', {}).get(var_name, {})
    
    # Get regions
    regions = var_config.get('regions', [None])
    
    return var_config, regions