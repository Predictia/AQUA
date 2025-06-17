"""
This module provides utilities for working with ecCodes, specifically
to retrieve attributes of GRIB parameters by their short names or param IDs.
It operates with caching to improve performance and handles preferentially GRIB2 format.
A tentative is done to access also GRIB1 format in case of errors with GRIB2, but it 
should be noted that GRIB1 is deprecated and not recommended for use.
"""
#import os
#import eccodes
#from packaging import version

import functools
from eccodes import codes_grib_new_from_samples, codes_set, codes_get, codes_release
from eccodes import CodesInternalError
from aqua.logger import log_configure
from aqua.exceptions import NoEcCodesShortNameError

# some eccodes shortnames are not unique: we need a manual mapping
NOT_UNIQUE_SHORTNAMES = {
    'tcc': [228164, 164]
}


@functools.cache
def _get_attrs_from_shortname(sn, grib_version="GRIB2"):
    """Get the attributes of a parameter by its short name.
    Args:
        sn (str): The short name to look up.
    Returns:
        dict: A dictionary containing the attributes of the parameter.
    """
    gid = codes_grib_new_from_samples(grib_version)
    if sn in NOT_UNIQUE_SHORTNAMES:
        # If the short name is special, we need to handle it differently
        # by using the first paramId in the list of not unique ones
        pid = NOT_UNIQUE_SHORTNAMES[sn][0]
        codes_set(gid, "paramId", pid)
    else:
        codes_set(gid, "shortName", sn)
        pid = codes_get(gid, "paramId", ktype=str)
    nm = codes_get(gid, "name")
    un = codes_get(gid, "units")
    #cf = codes_get(gid, "cfName")
    cfv = codes_get(gid, "cfVarName")
    codes_release(gid)
    return {
        'paramId': pid,
        'long_name': nm,
        'units': un,
        'shortName': sn,
        #'cfName': cf,
        'cfVarName': cfv
    }

@functools.cache
def _get_shortname_from_paramid(pid):
    """Get the attributes of a parameter by its paramId.

    Args:
        paramid (str): The parameter ID to look up.

    Returns:
        string: The short name associated with the given paramId.
    """
    gid = codes_grib_new_from_samples("GRIB2")
    codes_set(gid, "paramId", pid)
    sn = codes_get(gid, "shortName")
    codes_release(gid)
    return sn

def get_eccodes_attr(sn, loglevel='WARNING'):
    """
    Wrapper for _get_attrs_from_shorthName to retrieve attributes for a given short name.
    """
    logger = log_configure(log_level=loglevel, log_name='eccodes')

    # If sn is an integer or a string that can be converted to an integer, treat it as a paramId
    if isinstance(sn, int) or (isinstance(sn, str) and sn.isdigit()):
        logger.debug('Input is a paramId: %s', sn)
        sn = _get_shortname_from_paramid(sn)
    # extract the short name from the variable name if it starts with 'var'
    if sn.startswith("var"):
        logger.debug('Input is a variable name, extracting short name from: %s', sn)
        sn = _get_shortname_from_paramid(sn[3:])

    # Try to get attributes from GRIB2 first
    try:
        logger.debug('Retrieving attributes for short name: %s', sn)
        return _get_attrs_from_shortname(sn, grib_version="GRIB2")
    except CodesInternalError as e2:
        # If GRIB2 fails, try GRIB1
        try:
            logger.warning('Error retrieving attributes for short name %s: %s', sn, e2)
            logger.warning('Trying with GRIB1')
            return _get_attrs_from_shortname(sn, grib_version="GRIB1")
        except CodesInternalError as e1:
            raise NoEcCodesShortNameError(f"Cannot find any grib codes for ShortName {sn}") from e1
    
def get_eccodes_shortname(pid):
    """
    Wrapper for _get_shortname_from_paramid to retrieve the short name for a given paramId.
    """
    try:
        return _get_shortname_from_paramid(pid)
    except CodesInternalError as e:
        raise NoEcCodesShortNameError(f"Cannot find any grib codes for paramId {pid}") from e


# Currently not used
# def read_eccodes_dic(filename):
#     """
#     Reads an ecCodes definition file and returns its contents as a dictionary.

#     Parameters:
#     - filename (str): The name of the ecCodes definition file to read.

#     Returns:
#     - A dictionary containing the contents of the ecCodes definition file.
#     """
#     yaml = YAML(typ='rt')
#     fn = eccodes.codes_definition_path().split(':')[0]  # LUMI fix, take only first
#     fn = os.path.join(fn, 'grib2', filename)
#     with open(fn, "r", encoding='utf-8') as file:
#         text = file.read()
#     text = text.replace(" =", ":").replace('{', '').replace('}', '').replace(';', '').replace('\t', '    ')
#     return yaml.load(text)

# def eccodes_list_stripper(filename, tablelist):

#     """Eccodes definition file parser based on list
    
#     Args:
#         filename: The eccodes definition file
#         tablelist: The table that you want to update
#     """

#     with open(filename, "r", encoding='utf-8') as f:
#         for line in f:
#             line = line.replace(" =", "").replace('{', '').replace('}', '').replace(';', '').replace('\t', '#    ')
#             if not line.startswith("#"):
#                 tablelist.append(line.strip().replace("'", ""))
#     tablelist = tablelist[:-1]  # The last entry is no good
#     return tablelist

# def eccodes_dict_stripper(filename, tabledict):

#     """Alternative eccodes definition file parser based on dictionary
    
#     Args:
#         filename: The eccodes definition file
#         tabledict: The table that you want to update
#     """

#     with open(filename, "r", encoding='utf-8') as f:
#         for line in f:
#             line = line.replace(" =", "").replace('{', '').replace('}', '').replace(';', '').replace('\t', '$    ')
#             if not line.startswith("$") and not line.startswith("# "):
#                 #print(line)
#                 if line.startswith('#'):
#                     full_name = line.lstrip('#').strip()
#                     continue
#                 if full_name and line:
#                     #print(line)
#                     if not full_name in tabledict:
#                         tabledict[full_name] = line.strip('\n').strip(" ").strip("'")  # Remove quotes around the value
#                         full_name = None
#                     #else:
#                     #    print('double entry for' + full_name)
#     return tabledict

# def read_eccodes_def(filename):
#     """
#     Reads an ecCodes definition file and returns its keys as a list.

#     Parameters:
#         filename (str): The name of the ecCodes definition file to read.

#     Returns:
#         A list containing the keys of the ecCodes definition file.
#     """

#     # This allows to further extend the list of grib_version and tables to read
#     # when looking for eccodes definitions.
#     keylist = {'grib2': {
#                     'wmo': [],
#                     'ecmwf': []
#                 },
#                'grib1': {
#                    'ecmwf': []
#                }}
#     # keylist = {'grib2': {
#     #                 'wmo': {},
#     #                 'ecmwf': {}
#     #                 #'destine': {}
#     #             },
#     #            'grib1': {
#     #                'ecmwf': {}
#     #            }}

#     # OK I know this looks crazy
#     current = version.parse(eccodes.__version__)
#     check = version.parse("2.37.0")
#     if current >= check:
#         # ABSOLUTE CRAZY HACK
#         parts = (eccodes.__file__).split(os.sep)
#         lib_index = parts.index('lib')
#         fn_eccodes = os.path.join(os.sep.join(parts[:lib_index]), 'share/eccodes/definitions')
#     else:
#         fn_eccodes = eccodes.codes_definition_path().split(':')[0]  # LUMI fix, take only first


#     # WMO lists
#     fn = os.path.join(fn_eccodes, 'grib2', filename)
#     keylist['grib2']['wmo'] = eccodes_list_stripper(fn, keylist['grib2']['wmo'])
#     #keylist['grib2']['wmo'] = eccodes_dict_stripper(fn, keylist['grib2']['wmo'])

#     # ECMWF lists
#     for grib_version in ['grib2', 'grib1']:
#         fn = os.path.join(fn_eccodes, grib_version, 'localConcepts', 'ecmf', filename)
#         keylist[grib_version]['ecmwf'] = eccodes_list_stripper(fn, keylist[grib_version]['ecmwf'])
#         #keylist[grib_version]['ecmwf'] = eccodes_dict_stripper(fn, keylist[grib_version]['ecmwf'])
    
#     # DestinE lists
#     # for grib_version in ['grib2']:
#     #     fn = os.path.join(fn_eccodes, grib_version, 'localConcepts', 'destine', filename)
#     #     #keylist[grib_version]['destine'] = eccodes_list_stripper(fn, keylist[grib_version]['destine'])
#     #     keylist[grib_version]['destine'] = eccodes_dict_stripper(fn, keylist[grib_version]['destine'])

#     return keylist


# # Define this as a closure to avoid reading twice the same file
# def _init_get_eccodes_attr():
#     shortname = read_eccodes_def("shortName.def")
#     paramid = read_eccodes_def("paramId.def")
#     name = read_eccodes_def("name.def")
#     cfname = read_eccodes_def("cfName.def")
#     cfvarname = read_eccodes_def("cfVarName.def")
#     units = read_eccodes_def("units.def")

#     def _get_eccodes_attr(sn, loglevel='WARNING'):
#         """
#         Recover eccodes attributes for a given short name

#         Args:
#             shortname(str): the shortname to search
#             loglevel (str): the loggin level
#         Returns:
#             A dictionary containing param, long_name, units, short_name
#         """
#         logger = log_configure(log_level=loglevel, log_name='eccodes')
#         nonlocal shortname, paramid, name, cfname, cfvarname, units # noqa F824

#         if isinstance(sn, int) or (isinstance(sn, str) and sn.isdigit()):
#             sn = f'var{sn}'

#         for grib_version, tables in shortname.items():
#             for table in tables:
#                 try:
#                     if sn.startswith("var"):
#                         i = paramid[grib_version][table].index(sn[3:])
#                         #i = [key for key, value in paramid[grib_version][table].items() if value == sn[3:]][0]
#                     else:
#                         #indices = [key for key, value in shortname[grib_version][table].items() if value == sn]
#                         indices = [i for i, x in enumerate(shortname[grib_version][table]) if x == sn]
#                         if len(indices) > 1:
#                             logger.warning('ShortName %s has multiple grib codes associated: %s',
#                                            sn, [paramid[grib_version][table][i] for i in indices])
#                             logger.warning('AQUA will take the first so that %s -> %s, please set up a correct fix if this does not look right',  # noqa E501
#                                            sn, paramid[grib_version][table][indices[0]])
#                         i = indices[0]

#                     dic = {"paramId": paramid[grib_version][table][i],
#                            "long_name": name[grib_version][table][i],
#                            "units": units[grib_version][table][i],
#                            #"cfVarName": cfvarname[grib_version][table].get(i, shortname[grib_version][table][i]),
#                            "shortName": shortname[grib_version][table][i]}

#                     if 'grib1' in grib_version:
#                         logger.info('Variable %s is found in grib1 tables, please check if it is correct', shortname[grib_version][table][i]) # noqa E501
#                     elif 'ecmwf' in table:
#                         logger.debug('Variable %s is found in ECMWF local tables', shortname[grib_version][table][i])

#                     return dic

#                 except (ValueError, IndexError, KeyError):
#                     logger.debug('Not found shortname %s for gribversion %s, table %s', sn, grib_version, table)

#         logger.error('Cannot find any grib codes for ShortName %s, returning empty dictionary', sn)

#         return None

#     return _get_eccodes_attr


# get_eccodes_attr = _init_get_eccodes_attr()


# # Define this as a closure to avoid reading twice the same file
# def init_get_eccodes_shortname():
#     """
#     Recover eccodes shorthname from a given paramid

#     Args:
#         var(str, int): the variable name (a short_name or a paramid)

#     Returns:
#         A string containing the short_name
#     """
#     shortname = read_eccodes_def("shortName.def")
#     paramid = read_eccodes_def("paramId.def")

#     def _get_eccodes_shortname(var):
#         """
#         Allows to retrieve the shortname from the paramid

#         Args:
#             var(str, int): the variable name (a short_name or a paramid)

#         Returns:
#             A string containing the short_name
#         """
#         nonlocal shortname, paramid # noqa F824

#         if not str(var).isdigit():
#             return var
#         # If we have a digit we have to search for the shortname
#         # We loop over the available tables
#         for grib_version, tables in shortname.items():
#             for table, names in tables.items():
#                 try:
#                     i = paramid[grib_version][table].index(str(var))
#                     return names[i]
#                 except (ValueError, IndexError):
#                     continue
#         # Out of the loop, we have not found anything and we have no left table, error
#         raise NoEcCodesShortNameError(f'Cannot find any grib codes for paramid {var}')


#     return _get_eccodes_shortname
