#!/usr/bin/env python3
'''
PO.DAAC Cloud Download Subset

    This script can be used to download a subset of variables from netCDFs 
    stored on the PO.DAAC cloud. The script will search for files that intersect
    the given time range.

    This script requires that you have an Earth Data account and have setup a
    .netrc file in your home directory. Please see the below instructions on 
    how to do this. THese instructions were sourced from:
    https://github.com/podaac/data-subscriber

    1. Make sure you have an Earthdata account: [https://urs.earthdata.nasa.gov].
    
      Accounts are free to create and take just a moment to set up.
    
    2. Authentication setup
     The function below will allow Python scripts to log into any Earthdata 
     Login application programmatically.  To avoid being prompted for credentials 
     every time you run and also allow clients such as curl to log in, you can 
     add the following to a `.netrc` (`_netrc` on Windows) file in your home 
     directory:
    
    ```
    machine urs.earthdat.nasa.gov
        login <your username>
        password <your password>
    ```
    
    Make sure that this file is only readable by the current user or you will 
    receive an error stating "netrc access too permissive."
    
    `$ chmod 0600 ~/.netrc` 
    
    *You'll need to authenticate using the netrc method when running from command 
    line with [`papermill`](https://papermill.readthedocs.io/en/latest/). You can 
    log in manually by executing the cell below when running in the notebook 
    client in your browser.*

    Usage:
        podaac_cloud_download_subset.py <start_date> <end_date> <short_name> [options]
        podaac_cloud_download_subset.py -h | --help

    Options:
        start_date      First date to check for files.
                        This is inclusive and in YYYY-MM-DDTHH:mm:SS format.
        end_date        Last date to check for files.
                        This is NOT inclusive and in YYYY-MM-DDTHH:mm:SS format.
        short_name      PO.DAAC's short name for product. This can be found on
                        each product's PO.DAAC page. 
                        As an example, the CYGNSS L1 CDR short name is
                        CYGNSS_L1_CDR_V1.0
        --ext=ext       File extension of the files you are searching for on 
                        the PO.DAAC. [default: .nc4]
        --out-dir=out_dir 
                        Output directory for storing the downloaded netCDFs
                        [default: .]
        --variables=variables
                        Variables you want to extract from the files on the
                        PO.DAAC. If nothing is passed then the entire file will
                        be downloaded. The variable list should be comma 
                        seperated without spaces which will look like:
                        "sp_lat,sp_lon,ddm_nbrcs" [default: ] 
  
'''
from urllib.parse import urlencode, urlparse, quote
from os.path import isdir, join, basename, exists
from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError
from datetime import datetime
from docopt import docopt
from os import makedirs
from json import loads
import podaac_cloud_lib
import logging


'''
Setup logging configuration
'''
log_format = '%(asctime)s %(name)s %(levelname)s %(message)s'
date_format = '%H:%M:%S'
logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format)
_logger = logging.getLogger(__name__)


'''
Parse the command line arguments
'''
arguments = docopt(__doc__)
short_name = arguments['<short_name>']
out_dir = arguments['--out-dir']
extension = arguments['--ext']

# Create the list of variables to download and put it in the format needed by 
# the OPeNDAP server
variables = arguments['--variables']
variable_list = variables.split(',')

# Check if variables is empty
if variables:
    _logger.info('Downloading the following variables:')
    url_formatted_variables = '?dap4.ce=/'+variables.replace(',',';/')
    for var in variable_list:
        _logger.info(f'   {var}')
else:
    _logger.info('Downloading full files')
    url_formatted_variables = ''

# Read the time range and perform some sanity checks
dt_format = '%Y-%m-%dT%H:%M:%S'
try:
    datetime.strptime(arguments['<start_date>'],dt_format)
except:
    _logger.fatal("FAILURE: <start_date> ("+arguments['<start_date>']+ ") does not " \
          "match format " +dt_format + " \n")
    exit(1)
try:
    datetime.strptime(arguments['<end_date>'],dt_format)
except:
    _logger.fatal("FAILURE: <end_date> ("+arguments['<end_date>']+ ") does not " \
          "match format " +dt_format + " \n")
    exit(1)
temporal = arguments['<start_date>']+'Z'+','+arguments['<end_date>']+'Z'

'''
Static parameters
'''
bounding_extent='-180,-90,180,90'


'''
Authenticate with Earthdata Login and get a token
'''
# Setup the authentication and get a token
podaac_cloud_lib.setup_earthdata_login_auth()
token=podaac_cloud_lib.get_token(podaac_cloud_lib.edl_url)


'''
Search for the files on the PO.DAAC cloud
'''
params = {
    'page_size': 2000,
    'sort_key': "-start_date",
    'ShortName': short_name, 
    'temporal' : temporal,
    'token': token,
    'bounding_box': bounding_extent
}

# Get the query parameters as a string and then the complete search url:
query = urlencode(params)
url = "https://"+podaac_cloud_lib.cmr+"/search/granules.umm_json?"+query

# Open the URL
with urlopen(url) as f:
    results = loads(f.read().decode())

# Parse through the results and find all the OpenDAP links
urls_to_download = []
for r in results['items']:
    for u in r['umm']['RelatedUrls']:
         
        # Grab only the OpenDAP links
        if  ('Subtype' in u and u['Subtype'] == "OPENDAP DATA") and \
                '/drive/files/' not in u['URL']:
            
            # Find the url nested in the dictionary and store it in a list
            download_url = u['URL']
            urls_to_download.append(download_url)
            
'''
Download the files
'''
# Download the files. Do this after all the files have been found so we know
# the total number of files that need to be download     
total_files_to_download = len(urls_to_download)
num_downloaded = 0

if not urls_to_download:
    _logger.info("No files found to download")
    _logger.info("Please double check the colelction name ")
    exit(0)

custom_dap_url = f".dap{extension}{url_formatted_variables}"

# Check if the output directory exists. If not create it
if not isdir(out_dir):
    makedirs(out_dir)

for url in urls_to_download:

    num_downloaded += 1

    # Extract the file name from the URL for the output file
    out_file = join(out_dir, basename(urlparse(url).path)+extension)

    if exists(out_file):
        _logger.info(f"File {out_file} already exists. Skipping download. "
              f"({num_downloaded} of {total_files_to_download}) complete")
        continue

    # Append the URL with the custom DAP parameters and encode the URL
    url = url + custom_dap_url
    _logger.info("Downloading: " + url)
    encoded_url = quote(url, safe=':/')
    
    try:
        urlretrieve(encoded_url, out_file)
    except HTTPError as e:
        _logger.error("Received Error: " + str(e))
        _logger.error("There are a few potential causes of this: ")
        _logger.error("  1. Double check that all variables exist in the files and "
              " are spelled correctly")
        _logger.error("  2. If using the '.nc' extension try using the '.nc4' extension "
              "instead. NetCDF-4 can handle the int_8 data type used in some "
              "PO.DAAC files. netCDF-3 (.nc) often has issue with it.")
    
    _logger.info(f"Processed: ({num_downloaded} of {total_files_to_download})")

'''
Clean up the token that was generated
'''
podaac_cloud_lib.delete_token(token) 
