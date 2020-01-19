#!/usr/bin/python3

import sys
import os
import logging
import requests ## https://2.python-requests.org/en/master/
from config_local import myconfig

## disbale self-sigend certificate warning (InsecureRequestWarning)
import urllib3
urllib3.disable_warnings()


if len(sys.argv) != 2:
    print("usage: %s <output.txt>" % os.path.basename(sys.argv[0]))
    sys.exit(1)

outfile = sys.argv[1]
outfile = os.path.abspath(sys.argv[1])

if os.path.exists(outfile):
    raise RuntimeError(f"Output file already exists! {outfile}")


logging.basicConfig(level=logging.INFO)
piconf = myconfig['pimatic']


variables_url = "%s/variables" % piconf['api_url'].rstrip('/')

## SSL certificate
## https://2.python-requests.org/en/master/user/advanced/#ssl-cert-verification
## openssl s_client -showcerts -connect 192.168.1.7:8443 </dev/null
#r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), cert=('musca_pimatic.cert.pem', 'musca_pimatic.key.pem'))
#r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), cert=('cert.pem', 'privkey.pem'))
r = requests.get(variables_url, auth=(piconf['username'], piconf['password']), verify=False)

if not r.ok:
    raise RuntimeError((r.status_code, r.text))

r_json = r.json()
assert 'variables' in r_json
assert type(r_json['variables']) is list

with open(outfile, 'w') as fout:
    fout.write("## Enable rules creation by uncommenting the entries\n")
    for item in r_json['variables']:
        name = item['name']
        fout.write(f"#{name}\n")
