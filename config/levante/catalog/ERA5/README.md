# ERA5 daily variables, analysis

## Path_an = /work/bb1153/b382267/Observations_Zarr/ERA5/sf/an/1D/all

| Index        |  Short Name        | Units             | Long Name                 |    Path                 | 
| -------------|:----------------:  | ------------:     |--------------------------:|-----------------------:|
|   031     |   ci      |   (0 - 1)     |   Sea ice area fraction           |  Path_an/31.json         |
|   032     |   asn     |   (0 - 1)     |   Snow albedo                     | Path_an/         |
|   033     |   rsn     |   kg m-3      |   Snow density                    |  Path_an/         |
|   034     |   sst     |   K           |   Sea surface temperature         |  Path_an/34.json         |
|   035     |   istl1   |   K           |   Ice temperature layer 1         |  Path_an/         |
|   036     |   istl2   |   K           |   Ice temperature layer 2         |  Path_an/36.json         |
|   037     |   istl3   |   K           |   Ice temperature layer 3         |  Path_an/37.json         |
|   038     |   istl4   |   K           |   Ice temperature layer 4         |  Path_an/38.json         |
|   039     |   swvl1   |   m3m-3       |   Volumetric soil water layer 1   |  Path_an/         |
|   040     |   swvl2   |   m3 m-3      |   Volumetric soil water layer 2   |  Path_an/         |
|   041     |   swvl3   |   m3 m-3      |   Volumetric soil water layer 3   |  Path_an/         |
|   042     |   swvl4   |   m3 m-3      |   Volumetric soil water layer 4   |  Path_an/         |
|   134     |   sp      |   Pa          |   Surface pressure                |  Path_an/         |
|   136     |   tcw     |   kg m-2      |   Total column water              |  Path_an/136.json         |
|   137     |   tcwv    |   kg m-2      |   Total column vertically-integrated water vapour  |  Path_an/137.json         |
|   139     |   stl1    |   K           |   Soil temperature level 1        |  Path_an/139.json         |
|   141     |   sd      |   m of water equivalent       |      Snow depth   |  Path_an/141.json         |
|   151     |   msl     |   Pa          |   Mean sea level pressure         |  Path_an/151.json         |
|   164     |   tcc     |   (0 - 1)     |   Total cloud cover               |  Path_an/         |
|   165     |   10u     |   m s-1       |   10 metre U wind component       |  Path_an/165.json         |
|   166     |   10v     |   m s-1       |   10 metre V wind component       |  Path_an/166.json         |
|   167     |   2t      |   K           |   2 metre temperature             |  Path_an/167.json         |
|   168     |   2d      |   K           |   2 metre dewpoint temperature    |  Path_an/168.json         |
|   170     |   stl2    |   K           |   Soil temperature level 2        |  Path_an/170.json         |
|   183     |   stl3    |   K           |   Soil temperature level 3        |  Path_an/183.json         |
|   186     |   lcc     |   (0 - 1)     |   Low cloud cover                 |   Path_an/         |
|   187     |   mcc     |   (0 - 1)     |   Medium cloud cover              |  Path_an/         |
|   188     |   hcc     |   (0 - 1)     |   High cloud cover                |    Path_an/         |
|   198     |   src     |   m of water equivalent |  Skin reservoir content |    Path_an/         |
|   206     |   tco3    |   kg m-2      |   Total column ozone              |  Path_an/         |
|   235     |   skt     |   K           |   Skin temperature                |  Path_an/         |
|   236     |   stl4    |   K           |   Soil temperature level 4        |  Path_an/         |
|   238     |   tsn     |   K           |   Temperature of snow layer       |  Path_an/         |
|   243     |   fal     |   (0 - 1)     |   Forecast albedo                 |  Path_an/         |
|   244     |   fsr     |   m           |   Forecast surface roughness      |  Path_an/         |
|   245     |   flsr    |   ~           |   Forecast logarithm of surface roughness for heat |  Path_an/         |
|   502     |                  |              |                             |  Path_an/         |
|   503     |                  |              |                             |  Path_an/         |


Path to combined dataset: /work/bb1153/b382267/Observations_Zarr/ERA5/sf/an/1D/Combined/an_combined.json

                                  
# ERA5 daily variables, forecast

## Path_fc = /work/bb1153/b382267/Observations_Zarr/ERA5/sf/fc/1D/all

| Index        |  Short Name        | Units             | Long Name                 |   Path                 | 
| -------------|:----------------:  | ------------:     |--------------------------:|-----------------------:|
|   034     |    sst        |   K       |   Sea surface temperature                 |  Path_fc/         |
|   044     |    es         |   m of water equivalent    |     Snow evaporation     |  Path_fc/44.json         |
|   045     |    smlt       |   m of water equivalent       |   Snowmelt            |  Path_fc/45.json         |
|   049     |    ucurr      |   m s-1   |   U-component of current                  |  Path_fc/49.json         |
|   050     |    lspf       |   s       |   Large-scale precipitation fraction      |  Path_fc/50.json         |
|   057     |    uvb        |   J m-2   |   Downward UV radiation at the surface    |  Path_fc/57.json         |
|   059     |    cape       |   J kg-1  |   Convective available potential energy   |  Path_fc/59.json         |
|   066     |    lai_lv     |   m2 m-2  |   Leaf area index, low vegetation         |  Path_fc/         |
|   067     |    lai_hv     |   m2 m-2  |   Leaf area index, high vegetation        |  Path_fc/         |
|   078     |    tclw       |   kg m-2  |   Total column cloud liquid water         |  Path_fc/78.json         |
|   079     |    tciw       |   kg m-2  |   Total column cloud ice water            |  Path_fc/79.json         |
|   137     |    tcwv       |   kg m-2  |   Total column vertically-integrated water vapour    |  Path_fc/137.json         |
|   142     |    lsp        |   m       |   Large-scale precipitation               |  Path_fc/142.json         |
|   143     |    cp         |   m       |   Convective precipitation                |  Path_fc/143.json         |
|   144     |    sf         |   m of water equivalent      |   Snowfall             |  Path_fc/144.json         |
|   145     |    bld        |   J m-2   |   Boundary layer dissipation              |  Path_fc/145.json         |
|   146     |    sshf       |   J m-2   |   Surface sensible heat flux              |  Path_fc/146.json         |
|   147     |    slhf       |   J m-2   |   Surface latent heat flux                |  Path_fc/147.json         |
|   159     |    blh        |   m       |   Boundary layer height    |  Path_fc/159.json         |
|   164     |    tcc        |   (0 - 1) |    Total cloud cover   |   Path_fc/164.json         |
|   169     |    ssrd       |   J m-2   |   Surface short-wave (solar) radiation downwards      | Path_fc/169.json         | 
|   175     |    strd       |   J m-2   |   Surface long-wave (thermal) radiation downwards     |  Path_fc/175.json         |
|   176     |    ssr        |   J m-2   |   Surface net short-wave (solar) radiation    |  Path_fc/176.json         |
|   177     |    str        |   J m-2   |   Surface net long-wave (thermal) radiation   |  Path_fc/177.json         |
|   178     |    tsr        |   J m-2   |   Top net short-wave (solar) radiation    |  Path_fc/178.json         |
|   179     |    ttr        |   J m-2   |   Top net long-wave (thermal) radiation   | Path_fc/179.json         |
|   180     |    ewss       |   N m-2 s |   Eastward turbulent surface stress       |  Path_fc/180.json         |
|   181     |    nsss       |   N m-2 s |   Northward turbulent surface stress      |  Path_fc/181.json         |
|   182     |    e          |   m of water equivalent      |   Evaporation          |  Path_fc/         |
|   195     |    lgws       |   N m-2 s |    Eastward gravity wave surface stress   | Path_fc/195.json         |
|   196     |    mgws       |   N m-2 s |   Northward gravity wave surface stress   |  Path_fc/196.json         |
|   197     |    gwd        |   J m-2   |   Gravity wave dissipation                |  Path_fc/197.json         |
|   201     |    mx2t       |   K       |    Maximum temperature at 2 metres since previous post-processing   | Path_fc/201.json         |
|   202     |    mn2t       |   K       |   Minimum temperature at 2 metres since previous post-processing    |  Path_fc/202.json         |
|   205     |    ro         |   m       |   Runoff                                  |  Path_fc/205.json         |
|   208     |    tsrc       |   J m-2   |   Top net solar radiation, clear sky      | Path_fc/208.json         |
|   209     |    ttrc       |   J m-2   |    Top net thermal radiation, clear sky   |  Path_fc/209.json         |
|   210     |    ssrc       |   J m-2   |   Surface net short-wave (solar) radiation, clear sky                 |  Path_fc/210.json         |
|   211     |    strc       |   J m-2   |    Surface net long-wave (thermal) radiation, clear sky               |     Path_fc/         |
|   212     |    tisr       |   J m-2   |    TOA incident solar radiation           |  Path_fc/         |
|   228     |    tp         |   m       |    Total precipitation   |    Path_fc/228.json         |
|   239     |    csf        |   m of water equivalent       |   Convective snowfall |  Path_fc/         |
|   240     |    lsf        |   m of water equivalent       |   Large-scale snowfall|    Path_fc/         |
|   243     |    fal        |   (0 - 1) |   Forecast albedo    |  Path_fc/         |
|   244     |    fsr        |   m       |    Forecast surface roughness   |    Path_fc/         |
|   245     |    flsr       |   ~       |   Forecast logarithm of surface roughness for heat    | Path_fc/         |  
|   259     |          |           |       |  Path_an/         |  
|   277     |          |           |       |  Path_an/         |
|   278     |          |           |       |    Path_an/         |
|   279     |          |           |       |  Path_an/         |
|   285     |          |           |       |    Path_an/         |
|   385     |          |           |       |  Path_an/         |
|   386     |          |           |       |    Path_an/         |
|   474     |          |           |       |  Path_an/         |
|   475     |          |           |       |  Path_an/         |
|   476     |          |           |       |  Path_an/         |
|   477     |          |           |       |  Path_an/         |
|   507     |          |           |       |  Path_an/         |

                                                        
                                                       