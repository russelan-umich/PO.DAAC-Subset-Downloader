# PO.DAAC-Subset-Downloader
Tool for downloading a subset of variables from netCDFs stored on the PO.DAAC

## Setting up Earthdata account and .netrc
An Earthdata account and a valid .netrc on your local machine are required to run this script.
Please see the PO.DAAC's [Data Subscriber GitHub Page](https://github.com/podaac/data-subscriber?tab=readme-ov-file#step-1--get-earthdata-login) for the most up to date instructions.

## Additional Library Dependencies
This script requires your environment to include the 'requests' and 'docopt' libraries. These can either be installed manually into your environment or you can use the included Conda environment "podaac_subset_downloader_env_{NAME_OF_OS}.yml". The Conda environment can be created from file with:
`conda env create -f podaac_subset_downloader_env{NAME_OF_OS}.yml`
For more detailed instructions please see below


## Install Instructions
1. If you don’t already have a Conda or Python environment, here are instructions for installing Miniconda to help manage your Python environment and load the precreated environment files: [Miniconda Install](https://docs.anaconda.com/miniconda/install/#quick-command-line-install)
2. Setup the netrc using these [PO.DAAC instructions](https://github.com/podaac/data-subscriber?tab=readme-ov-file#step-1--get-earthdata-login])
3. Make sure that it you are on Mac or Linux you set the permission on the .netrc file to 600 by using:
   - `chmod 0600 ~/.netrc`
4. Setup GitHub either on the [command line](https://docs.github.com/en/get-started/getting-started-with-git/set-up-git) or using the [GUI Desktop environment](https://github.com/apps/desktop).
   - The desktop environment is more beginner friendly option, but not natively available on Linux platforms
5. Pull down the repo on to your local machine to your desired location either using the instructions with desktop client or the command line with the following:
   - `git clone https://github.com/russelan-umich/PO.DAAC-Subset-Downloader.git .`
6. Enter a command-line session to create the Python environment (see [Python Environment Setup](#python-environment-setup) for more details).
   - On Windows, it is easiest to use the Anaconda Powershell Prompt that comes with Miniconda to access to setup and run this program
7. Run a sample command.
   - Linux / Mac
     - `./podaac_cloud_download_subset.py 2021-01-01T00:00:00 2021-01-03T00:00:00 CYGNSS_L3_V3.2 --out-dir . --variables wind_speed`
   - Windows
     - `python podaac_cloud_download_subset.py 2021-01-01T00:00:00 2021-01-03T00:00:00 CYGNSS_L3_V3.2 --out-dir . --variables wind_speed`
    

## Python Environment Setup
### Load from Conda Environment 
- `conda env create -f podaac_subset_downloader_env_{NAME_OF_OS}.yml`
  - Replace `{NAME_OF_OS}` with either linux, mac, or windows
-  `conda activate podaac_subset_downloader_env`
### Manual Package Install with Conda
- `conda create --name podaac_subset_downloader_env  python=3.12`
- `conda activate podaac_subset_downloader_env`
- `conda install requests docopt`

### Manual Package Install with PIP in a Pre-existing Python Environment
- `pip install requests docopt`

## Common Issues
- `netrc.NetrcParseError: ~/.netrc access too permissive: access permissions must restrict access to only the owner`
  - If you receive this on Mac on Linux you need to set the permissions on ~/.netrc to 600, by using `chmod 0600 ~/.netrc`

## Helpful Notes
- List all the current conda environment
  - `conda env list`
- Update Conda
  - `conda update --all`
- [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf)
