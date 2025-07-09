import cartopy.crs as ccrs

projections_maps = {
    "plate_carree": ccrs.PlateCarree,
    "mercator": ccrs.Mercator,
    "robinson": ccrs.Robinson,
    "mollweide": ccrs.Mollweide,
    "orthographic": ccrs.Orthographic,
    "lambert_conformal": ccrs.LambertConformal,
    "albers_equal_area": ccrs.AlbersEqualArea,
    "nh_polar_stereo": ccrs.NorthPolarStereo,
    "sh_polar_stereo": ccrs.SouthPolarStereo,
    "eckert_iv": ccrs.EckertIV,
    "eckert_vi": ccrs.EckertVI,
    "equal_earth": ccrs.EqualEarth,
    "azimuthal_equidistant": ccrs.AzimuthalEquidistant,
    "gnomonic": ccrs.Gnomonic,
    "sinusoidal": ccrs.Sinusoidal,
}

def get_projection(projname: str, **kwargs) -> ccrs.Projection:
    """
    Return a Cartopy projection by name.

    Args:
        projname (str): Name of the projection.
        **kwargs: Additional keyword arguments passed to the projection class.

    Returns:
        cartopy.crs.Projection: An instance of the projection.
    """
    projname = projname.lower()
    if projname not in projections_maps:
        raise ValueError(f"Unsupported projection: '{projname}'. "
                         f"Available options are: {list(projections_maps.keys())}")
    
    projection_class = projections_maps[projname]
    return projection_class(**kwargs)
