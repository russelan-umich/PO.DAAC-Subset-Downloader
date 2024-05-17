#!/usr/bin/env python3

# Library for accessing the CYGNSS data through the PO.DAAC Cloud
# Before using this library, make sure you have an Earthdata account: 
#    [https://urs.earthdata.nasa.gov].

# Most of this library is pulled from the PO.DAAC GitHub PO.DAAC Cloud tutorial
# https://github.com/podaac/sentinel6/blob/master/Access_Sentinel6MF_usingshortname.py
#
from http.cookiejar import CookieJar
from requests.auth import HTTPBasicAuth
from urllib import request
import requests
import socket 
import netrc
import json

# The lines below are to get the IP address. You can make this static and 
# assign a fixed value to the IPAddr variable.
#
host_name = socket.gethostname()    
ip_addr = socket.gethostbyname(host_name)

# Setup the URLS to the PO.DAAC
edl="urs.earthdata.nasa.gov"
cmr="cmr.earthdata.nasa.gov" 
token_url="https://"+cmr+"/legacy-services/rest/tokens"
edl_url="https://"+edl+"/api/users"

def setup_earthdata_login_auth():
    """
    Set up the request library so that it authenticates against the given 
    Earthdata Login  endpoint and is able to track cookies between requests.  
    This looks in the .netrc file first and if no credentials are found, it 
    prompts for them. Valid endpoints include:
        urs.earthdata.nasa.gov - Earthdata Login production (edl)
    """
    try:
        username, _, password = netrc.netrc().authenticators(edl)
    except (FileNotFoundError, TypeError):
        # FileNotFound = There's no .netrc file
        # TypeError = The endpoint isn't in the netrc file, causing the above to try unpacking None
        print("There's no .netrc file or the The endpoint isn't in the netrc file")

    manager = request.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, edl, username, password)
    auth = request.HTTPBasicAuthHandler(manager)

    jar = CookieJar()
    processor = request.HTTPCookieProcessor(jar)
    opener = request.build_opener(auth, processor)
    request.install_opener(opener)

###############################################################################
# GET TOKEN FROM CMR 
###############################################################################
    
def list_tokens(url: str):
    try:
        tokens = []
        username, _, password = netrc.netrc().authenticators(edl)
        headers: Dict = {'Accept': 'application/json'}  # noqa E501
        resp = requests.get(url+"/tokens", headers=headers, auth=HTTPBasicAuth(username, password))
        response_content = json.loads(resp.content)

        for x in response_content:
            tokens.append(x['access_token'])

    except:  # noqa E722
        print("Error getting the token - check user name and password", exc_info=True)
    return tokens

def get_token( url: str ) -> str:
    try:
        token: str = ''
        username, _, password = netrc.netrc().authenticators(edl)
        headers: Dict = {'Accept': 'application/json'}  # noqa E501


        resp = requests.post(url+"/token", headers=headers, auth=HTTPBasicAuth(username, password))
        response_content: Dict = json.loads(resp.content)
        if "error" in response_content:
            if response_content["error"] == "max_token_limit":
                print("Max tokens acquired from URS. Using existing token")
                tokens=list_tokens(url)
                return tokens[0]
        token = response_content['access_token']

    # Add better error handling there
    # Max tokens
    # Wrong Username/Passsword
    # Other
    except Exception as e:  # noqa E722
        print("Error getting the token - check user name and password")
        print(e)
    return token

###############################################################################
# DELETE TOKEN FROM CMR 
###############################################################################
def delete_token(token: str) -> None:
	try:
		headers: Dict = {'Content-Type': 'application/xml','Accept': 'application/json'}
		url = '{}/{}'.format(token_url, token)
		resp = requests.request('DELETE', url, headers=headers)
		if resp.status_code == 204:
			print("CMR token successfully deleted")
		else:
			print("CMR token deleting failed.")
	except:
		print("Error deleting the token")
