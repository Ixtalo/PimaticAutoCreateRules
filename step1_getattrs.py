#!/usr/bin/python3

import logging
import os
import requests ## https://2.python-requests.org/en/master/
from config_local import myconfig


"""
Filename of the output file
"""
OUTFILE = 'step1_getattrs.txt'


###############################################################################
###############################################################################
###############################################################################


if os.path.exists(OUTFILE):
    raise RuntimeError(f"Output file already exists! {OUTFILE}")


logging.basicConfig(level=logging.INFO)
piconf = myconfig['pimatic']


variables_url = "%s/variables" % piconf['api_url'].rstrip('/')

## SSL certificate
## https://2.python-requests.org/en/master/user/advanced/#ssl-cert-verification
## openssl s_client -showcerts -connect 192.168.1.7:8443 </dev/null
#r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), cert=('musca_pimatic.cert.pem', 'musca_pimatic.key.pem'))
#r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), cert=('cert.pem', 'privkey.pem'))
r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), verify=False)

r_json = r.json()
assert 'variables' in r_json
assert type(r_json['variables']) is list

with open(OUTFILE, 'w') as fout:
    fout.write("## Enable rules creation by uncommenting the entries\n")
    for item in r_json['variables']:
        name = item['name']
        fout.write(f"#{name}\n")
