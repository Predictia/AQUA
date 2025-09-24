"""Module containing general utility functions for AQUA"""

from __future__ import annotations
import os
import random
import string
import re
import sys
import numpy as np
import xarray as xr
import pandas as pd
from glob import glob
from pypdf import PdfReader, PdfWriter
from PIL import Image, PngImagePlugin
from IPython.display import display, Image as IPImage, FileLink
from aqua.logger import log_configure
from aqua.version import __version__ as version


def generate_random_string(length):
    """
    Generate a random string of lowercase and uppercase letters and digits
    """

    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return random_string


def to_list(arg):
    """
    Converts the input to a list.
    - Returns [] if input is None.
    - Returns the list itself if input is already a list.
    - Converts tuples, sets, and dictionaries to a list.
    - Wraps other types in a single-element list.

    Parameters:
    arg: The input object to convert.

    Returns:
    list: A list representation of the input.
    """
    if arg is None:  # Preserve None
        return []
    if isinstance(arg, list):  # Already a list
        return arg
    if isinstance(arg, (tuple, set)):  # Convert tuples and sets to a list
        return list(arg)
    if isinstance(arg, dict):  # Convert dictionary keys to a list
        return list(arg.keys())
    return [arg]


def files_exist(path):
    """
    Verify that a list or path includes files
    """

    # Iterate over each pattern and check for the existence of matching files
    for p in to_list(path):
        if glob(p):  # If glob finds at least one match, return True
            return True

    return False


def get_arg(args, arg, default):
    """
    Support function to get arguments

    Args:
        args: the arguments
        arg: the argument to get
        default: the default value

    Returns:
        The argument value or the default value
    """

    res = getattr(args, arg)
    if not res:
        res = default
    return res


def create_folder(folder, loglevel="WARNING"):
    """
    Create a folder if it does not exist

    Args:
        folder (str): the folder to create
        loglevel (str): the log level

    Returns:
        None
    """
    logger = log_configure(loglevel, 'create_folder')

    if not os.path.exists(folder):
        logger.info('Creating folder %s', folder)
        os.makedirs(folder, exist_ok=True)
    else:
        logger.info('Folder %s already exists', folder)


def file_is_complete(filename, loglevel='WARNING'):
    """
    Basic check to see if file exists and that includes values
    which are not NaN in its first variabiles
    Return a boolean that can be used as a flag for further operation
    A loglevel can be passed for tune the logging properties

    Args:
        filename: a string with the filename
        loglevel: the log level

    Returns
        A boolean flag (True for file ok, False for file corrupted)
    """

    logger = log_configure(loglevel, 'file_is_complete')

    # check file existence
    if not os.path.isfile(filename):
        logger.info('File %s not found...', filename)
        return False

    logger.info('File %s is found...', filename)

    # check opening
    try:
        xfield = xr.open_dataset(filename)

        # check variables
        if len(xfield.data_vars) == 0:
            logger.error('File %s has no variables!', filename)
            return False

        # check on a single variable
        varname = list(xfield.data_vars)[0]

        # all NaN case
        if xfield[varname].isnull().all():

            # case of a mindate on all NaN single files
            mindate = xfield[varname].attrs.get('mindate')
            if mindate is not None:
                logger.warning('All NaN and mindate found: %s', mindate)
                if xfield[varname].time.max() < np.datetime64(mindate):
                    logger.info('File %s is full of NaN but it is ok according to mindate', filename)
                    return True

                logger.error('File %s is full of NaN and not ok according to mindate', filename)
                return False

            logger.error('File %s is empty or full of NaN! Recomputing...', filename)
            return False

        # some NaN case
        mydims = [dim for dim in xfield[varname].dims if dim != 'time']
        nan_count = np.isnan(xfield[varname]).sum(dim=mydims)
        if all(value == nan_count[0] for value in nan_count):
            logger.info('File %s seems ok!', filename)
            return True

        # case of a mindate on some NaN
        mindate = xfield[varname].attrs.get('mindate')
        if mindate is not None:
            logger.warning('Some NaN and mindate found: %s', mindate)
            last_nan = xfield.time[np.where(nan_count == nan_count[0])].max()
            if np.datetime64(mindate) > last_nan:
                logger.info('File %s has some of NaN up to %s but it is ok according to mindate %s',
                            filename, last_nan.values, mindate)
                return True

            logger.error('File %s has some NaN bit it is not ok according to mindate', filename)
            return False

        logger.error('File %s has at least one time step with NaN! Recomputing...', filename)
        return False

    except Exception as e:
        logger.error('Something wrong with file %s! Recomputing... Error: %s', filename, e)
        return False


def find_vert_coord(ds):
    """
    Identify the vertical coordinate name(s) based on coordinate units. Returns always a list.
    The list will be empty if none found.
    """
    vert_coord = [x for x in ds.coords if ds.coords[x].attrs.get("units") in ["Pa", "hPa", "m", "km", "Km", "cm", ""]]
    return vert_coord


def extract_literal_and_numeric(text):
    """
    Given a string, extract its literal and numeric part
    """
    # Using regular expression to find alphabetical characters and digits in the text
    match = re.search(r'(\d*)([A-Za-z]+)', text)

    if match:
        # If a match is found, return the literal and numeric parts
        literal_part = match.group(2)
        numeric_part = match.group(1)
        if not numeric_part:
            numeric_part = 1
        return literal_part, int(numeric_part)
    else:
        # If no match is found, return None or handle it accordingly
        return None, None


def add_pdf_metadata(filename: str,
                     metadata_value: str | dict,
                     metadata_name: str = '/Description',
                     old_metadata: bool = True,
                     loglevel: str = 'WARNING'):
    """
    Open a pdf and add new metadata.

    Args:
        filename (str): the filename of the pdf.
                        It must be a valid full path.
        metadata_value (str | dict): the value(s) of the new metadata.
        metadata_name (str): the name of the new metadata.
                            Default is '/Description'.
        old_metadata (bool): if True, the old metadata will be kept.
                            Default is True.
        loglevel (str): the log level. Default is 'WARNING'.

    Raise:
        FileNotFoundError: if the file does not exist.
    """
    logger = log_configure(loglevel, 'add_pdf_metadata')

    if not os.path.isfile(filename):
        raise FileNotFoundError(f'File {filename} not found')

    # Ensure metadata_name starts with '/'
    if metadata_name and not metadata_name.startswith('/'):
        logger.debug('metadata_name does not start with "/". Adding it...')
        metadata_name = '/' + metadata_name

    pdf_reader = PdfReader(filename)
    pdf_writer = PdfWriter()

    # Add existing pages to the new PDF
    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    # Keep old metadata if required
    if old_metadata:
        logger.debug('Keeping old metadata')
        metadata = pdf_reader.metadata
        pdf_writer.add_metadata(metadata)

    # Add the new metadata
    if isinstance(metadata_value, dict):
        metadata_value = {f'/{k}' if not k.startswith('/') else k: v for k, v in metadata_value.items()}  # Ensure keys start with '/'
        pdf_writer.add_metadata(metadata_value)
    else:
        pdf_writer.add_metadata({metadata_name: metadata_value})

    # Overwrite input PDF
    with open(filename, 'wb') as f:
        pdf_writer.write(f)


def add_png_metadata(png_path: str, metadata: dict, loglevel: str = 'WARNING'):
    """
    Add metadata to a PNG image file.

    Args:
        png_path (str): The path to the PNG image file.
        metadata (dict): A dictionary of metadata to add to the PNG file.
                         Note: Metadata keys do not need a '/' prefix.
        loglevel (str): The log level. Default is 'WARNING'.
    """
    logger = log_configure(loglevel, 'add_png_metadata')

    if not os.path.isfile(png_path):
        raise FileNotFoundError(f'File {png_path} not found')

    image = Image.open(png_path)

    # Create a dictionary for the PNG metadata
    png_info = PngImagePlugin.PngInfo()

    # Add the new metadata
    for key, value in metadata.items():
        png_info.add_text(key, str(value))
        logger.debug(f'Adding metadata: {key} = {value}')

    # Save the file with the new metadata
    image.save(png_path, "PNG", pnginfo=png_info)
    logger.info(f"Metadata added to PNG: {png_path}")


def open_image(file_path: str, loglevel: str = 'WARNING') -> dict:
    """
    Open an image file (PNG or PDF), log its metadata, and display a link to the file in the notebook.

    Args:
        file_path (str): The path to the image file.
        loglevel (str): The log level. Default is 'WARNING'.

    Returns:
        dict: The metadata of the image file with normalized keys (lowercase and without prefixes).
    """
    logger = log_configure(loglevel, 'open_image')

    # Ensure the file exists
    if not os.path.isfile(file_path):
        logger.error(f"The file {file_path} does not exist.")
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    metadata = {}

    # Determine the file extension using endswith()
    if file_path.lower().endswith('.png'):
        # Open the PNG file and read the metadata
        image = Image.open(file_path)
        metadata = image.info

        # Normalize keys to lowercase and remove any prefixes
        metadata = {normalize_key(key): normalize_value(value) for key, value in metadata.items()}

        # Log the metadata
        logger.info("PNG Metadata:")
        for key, value in metadata.items():
            logger.info(f"{key}: {value}")

    elif file_path.lower().endswith('.pdf'):
        # Open the PDF file and read the metadata
        pdf_reader = PdfReader(file_path)
        metadata = pdf_reader.metadata

        # Convert PyPDF2 metadata object to dictionary and normalize keys
        metadata = {normalize_key(key): normalize_value(value) for key, value in metadata.items() if value is not None}

        # Log the metadata
        logger.info("PDF Metadata:")
        for key, value in metadata.items():
            logger.info(f"{key}: {value}")

    else:
        logger.error(f"Unsupported file type: {file_path}")
        raise ValueError(f"Unsupported file type: {file_path}")

    # Provide a FileLink to the file
    display(FileLink(file_path))
    logger.info(f"Displayed file link for: {file_path}")

    return metadata


def normalize_key(key: str) -> str:
    """
    Normalize metadata key by removing leading '/' and converting to lowercase.
    """
    return key.lstrip('/').lower()


def normalize_value(value):
    """
    Normalize metadata values. If the value is a dictionary or dictionary-like string, normalize its keys.

    Args:
        value: Metadata value to normalize.

    Returns:
        Normalized value.
    """
    # Check if value is a dictionary, normalize its keys
    if isinstance(value, dict):
        return {normalize_key(k): normalize_value(v) for k, v in value.items()}
    
    # Check if value is a string that looks like a dictionary-like structure
    if isinstance(value, str):
        if re.match(r"^\{.*\}$", value.strip()):
            try:
                # Convert dictionary-like string into an actual dictionary
                parsed_value = eval(value, {"__builtins__": None}, {})
                if isinstance(parsed_value, dict):
                    # Normalize the keys if it is a dictionary
                    return {normalize_key(k): normalize_value(v) for k, v in parsed_value.items()}
            except Exception as e:
                # Log parsing errors and return the original string if parsing fails
                log_configure('WARNING', 'normalize_value').warning(f"Failed to parse string as dictionary: {e}")
    
    # Return the value as-is if it can't be processed further
    return value


def update_metadata(metadata: dict = None, additional_metadata: dict = None) -> dict:
    """
    Update the provided metadata dictionary with the current date, time, aqua package version,
    and additional diagnostic information.

    Args:
        metadata (dict, optional): The original metadata dictionary.
        additional_metadata (dict, optional): A dictionary containing additional metadata fields (e.g., diagnostic, model, experiment, etc.).

    Returns:
        dict: The updated metadata dictionary.
    """
    if metadata is None:
        metadata = {}

    # Add current date and time to metadata
    now = pd.Timestamp.now()
    date_now = now.strftime("%Y-%m-%d %H:%M:%S")
    metadata['timestamp'] = date_now
    metadata['aqua_version'] = version

    # Add additional metadata fields
    if additional_metadata:
        metadata.update(additional_metadata)

    return metadata


def extract_attrs(data, attr):
    """Extract attribute(s) from dataset or list of datasets.
    Args:
        data (xarray.Dataset or list of xarray.Dataset): Dataset(s) to extract
        attr (str): Attribute name to extract.
        Returns:
            list: List of attribute values from the dataset(s).
    """
    if data is None:
        return None
    if isinstance(data, list):
        return [getattr(ds, attr, None) for ds in data]
    return getattr(data, attr, None)


def username():
    """
    Retrieves the current user's username from the 'USER' environment variable.
    """
    user = os.getenv('USER')
    if user is None:
        raise EnvironmentError("The 'USER' environment variable is not set.")
    return user

class HiddenPrints:
    # from stackoverflow https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print#:~:text=If%20you%20don't%20want,the%20top%20of%20the%20file. # noqa
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout