import cartopy.crs as ccrs

projections_maps = {
    "plate_carree": ccrs.PlateCarree,
    "lambert_cylindrical": ccrs.LambertCylindrical,
    "lambert_cylindrical_equal_area": ccrs.LambertCylindricalEqualArea,
    "mercator": ccrs.Mercator,
    "nearside": ccrs.NearsidePerspective,
    "geostationary": ccrs.Geostationary,
    "interrupt_gh": ccrs.InterruptedGoodeHomolosine,
    "robinson": ccrs.Robinson,
    "mollweide": ccrs.Mollweide,
    "orthographic": ccrs.Orthographic,
    "lambert_conformal": ccrs.LambertConformal,
    "albers_equal_area": ccrs.AlbersEqualArea,
    "lambert_equal_area": ccrs.LambertAzimuthalEqualArea,
    "nh_polar_stereo": ccrs.NorthPolarStereo,
    "sh_polar_stereo": ccrs.SouthPolarStereo,
    "eckert_iv": ccrs.EckertIV,
    "eckert_vi": ccrs.EckertVI,
    "equal_earth": ccrs.EqualEarth,
    "azimuthal_equidistant": ccrs.AzimuthalEquidistant,
    "gnomonic": ccrs.Gnomonic,
    "sinusoidal": ccrs.Sinusoidal,
    "stereographic": ccrs.Stereographic
    }

def get_projection(projname: str, **kwargs) -> ccrs.Projection:
    """
    Return a Cartopy projection by name. Refer to the Cartopy 
    documentation (https://scitools.org.uk/cartopy/) to review the 
    supported keyword arguments for each projection class.

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
