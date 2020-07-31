#!/usr/bin/python3

import sys
import os
import logging
import requests  ## https://2.python-requests.org/en/master/
from config_local import myconfig

## disbale self-sigend certificate warning (InsecureRequestWarning)
import urllib3

urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO)
piconf = myconfig['pimatic']
rules_url = "%s/rules" % piconf['api_url'].rstrip('/')
rule_prefix = myconfig['rule_prefix']

r = requests.get("%s/rules" % piconf['api_url'].rstrip('/'), auth=(piconf['username'], piconf['password']),
                 verify=False)
if not r.ok:
    raise RuntimeError((r.status_code, r.text))

rule_prefix = 'notupdated-'

logging.info("Rule prefix for deletion: %s", rule_prefix)

## safety
assert rule_prefix

r_json = r.json()
for rule in r_json['rules']:
    rule_id = rule['id']
    if rule_id.startswith(rule_prefix):
        logging.info("Deleting rule '%s' ...", rule_id)
        r = requests.delete(f"{rules_url}/{rule_id}",
                            auth=(piconf['username'], piconf['password']),
                            verify=False)
        if not r.ok:
            logging.error(r.text)
