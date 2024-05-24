# PO.DAAC-Subset-Downloader
Tool for downloading a subset of variables from netCDFs stored on the PO.DAAC

## Setting up Earthdata account and .netrc
An Earthdata account and a valid .netrc on your local machine are required to run this script.
Please see the PO.DAAC's [Data Subscriber GitHub Page](https://github.com/podaac/data-subscriber?tab=readme-ov-file#step-1--get-earthdata-login) for the most up to date instructions.

## Additional Library Dependencies
This script requires your environment to include the 'requests' and 'docopt' libraries. These can either be installed manually into your environment or you can use the included Conda environment "podaac_subset_downloader_env.yml". The Conda environment can be created from file with:
`conda env create -f podaac_subset_downloader_env.yml`
