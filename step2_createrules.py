#!/usr/bin/python3

import logging
from string import ascii_letters, digits
from json import dumps
import requests ## https://2.python-requests.org/en/master/
from config_local import myconfig


"""
Filename of the output from step 1.
"""
INFILE = 'step1_getattrs.txt'

"""
Flag wheter to overwrite rules (HTTP PATCH)
"""
OVERWRITE_RULES = False

"""
Pimatic time-span string, e.g. "24 hours"
"""
TIME_PERIOD = '24 hours'


###############################################################################
###############################################################################
###############################################################################


logging.basicConfig(level=logging.INFO)
piconf = myconfig['pimatic']
rules_url = "%s/rules" % piconf['api_url'].rstrip('/')


## collect DeviceIds and AttributeNames from CSV from step1
dev2attr = {}
with open(INFILE, 'r') as fin:
    for line in fin:
        if line.strip().startswith('#'):
            continue
        dev, attr = line.split('.', 1)
        dev2attr[dev.strip()] = attr.strip()

logging.info("Amount of active items: %d", len(dev2attr))

## string translation table for German
detrans = str.maketrans({
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ß': 'ss',
    '.': '_'
})

## process each active item (device.attribute)
for dev, attr in dev2attr.items():
    logging.info('Processing %s.%s ...', dev, attr)

    ## create a valid rule ID
    dev_slug = dev.translate(detrans)
    dev_slug = ''.join([c.lower() for c in dev_slug if c in digits+ascii_letters+'_-'])
    attr_slug = attr.translate(detrans)
    attr_slug = ''.join([c.lower() for c in attr_slug if c in digits+ascii_letters+'_-'])
    ruleid = f"notupdated-{dev_slug}-{attr_slug}"

    ## rule parameters
    ## https://www.pimatic.org/docs/pimatic/lib/api/
    conditionToken = f'''when {attr} of {dev} was not updated for {TIME_PERIOD}'''
    actionsToken = f'''mail to:"mailast@web.de" subject:"[SmartHome] Problem: {ruleid}" text:"{dev}.{attr} was not updated for {TIME_PERIOD}"'''
    payload = {
        "rule": {
            "name": f"NotUpdated {dev}.{attr}",
            "ruleString": f"{conditionToken} then {actionsToken}",
            "active": True,
            "logging": True
        }
    }

    ## check if rule already exists
    r = requests.get(f"{rules_url}/{ruleid}",
                     auth=(piconf['username'], piconf['password']),
                     verify=False
                     )
    if r.status_code == 200:
        ## exists already...
        if OVERWRITE_RULES:
            logging.warning("Rule %s exists already! Overwriting...", ruleid)
            r = requests.patch(f"{rules_url}/{ruleid}",
                               data=dumps(payload),
                               headers={'Content-Type': 'application/json'},
                               auth=(piconf['username'], piconf['password']),
                               verify=False
                               )
            print(r)
        else:
            logging.warning("Rule %s exists already! Skipping.", ruleid)
    else:
        logging.info("Adding rule %s ...", ruleid)
        r = requests.post(f"{rules_url}/{ruleid}",
                          data=dumps(payload),
                          headers={'Content-Type': 'application/json'},
                          auth=(piconf['username'], piconf['password']),
                          verify=False
                          )
        print(r)
