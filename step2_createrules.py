#!/usr/bin/python3

import sys
import os
import logging
from string import ascii_letters, digits
from json import dumps
import requests ## https://2.python-requests.org/en/master/
from config_local import myconfig

## disbale self-sigend certificate warning (InsecureRequestWarning)
import urllib3
urllib3.disable_warnings()


if len(sys.argv) != 2:
    print("usage: %s <input.txt>" % os.path.basename(sys.argv[0]))
    sys.exit(1)

inputfile = sys.argv[1]
inputfile = os.path.abspath(sys.argv[1])


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
piconf = myconfig['pimatic']
rules_url = "%s/rules" % piconf['api_url'].rstrip('/')
rule_prefix = myconfig['rule_prefix']
rules_overwrite_flag = myconfig['overwrite_rules']
mail_receiver = myconfig['mail_receiver']
default_time = myconfig['default_time_period']


## collect DeviceIds and AttributeNames from CSV from step1
dev2attr = {}
with open(inputfile, 'r') as fin:
    for line in fin:
        line = line.strip()
        if line.startswith('#'):
            continue
        ## e.g., wemosd1_og2_treppe.Temperatur
        dev, attr = line.split('.', 1)
        dev = dev.strip()
        attr = attr.strip()

        ## e.g., #wemosd1_og2_treppe.Temperatur;12h
        if ';' in attr:
            attr, duration = attr.split(';')
        else:
            duration = default_time

        dev2attr[dev] = (attr, duration)

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
for dev, (attr, duration) in dev2attr.items():
    logging.info('Processing %s.%s ...', dev, attr)

    ## create a valid rule ID
    ## must be lowercase and contain only plain ASCII characters
    dev_slug = dev.translate(detrans)
    dev_slug = ''.join([c.lower() for c in dev_slug if c in digits+ascii_letters+'_-'])
    attr_slug = attr.translate(detrans)
    attr_slug = ''.join([c.lower() for c in attr_slug if c in digits+ascii_letters+'_-'])
    rule_id = f"{rule_prefix}-{dev_slug}-{attr_slug}".lower()

    ## rule parameters
    ## https://www.pimatic.org/docs/pimatic/lib/api/
    conditionToken = f'''when {attr} of {dev} was not updated for {duration}'''
    actionsToken = f'''mail to:"{mail_receiver}" subject:"[SmartHome] Problem: {rule_id}" text:"{dev}.{attr} was not updated for {duration}"'''
    payload = {
        "rule": {
            "name": f"{rule_prefix}_{dev}.{attr}",
            "ruleString": f"{conditionToken} then {actionsToken}",
            "active": True,
            "logging": True
        }
    }

    logging.debug('payload: %s', payload)

    ## check if rule already exists
    logging.debug("Checking if rule '%s' exist already ...", rule_id)
    r = requests.get(f"{rules_url}/{rule_id}",
                     auth=(piconf['username'], piconf['password']),
                     verify=False
                     )
    if r.status_code == 200:
        ## exists already...
        if rules_overwrite_flag:
            logging.warning("Rule %s exists already! Overwriting...", rule_id)
            r = requests.patch(f"{rules_url}/{rule_id}",
                               data=dumps(payload),
                               headers={'Content-Type': 'application/json'},
                               auth=(piconf['username'], piconf['password']),
                               verify=False
                               )
            if not r.ok:
                logging.error(r.text)
        else:
            logging.warning("Rule %s exists already! Skipping.", rule_id)
    else:
        logging.info("Adding rule %s ...", rule_id)
        r = requests.post(f"{rules_url}/{rule_id}",
                          data=dumps(payload),
                          headers={'Content-Type': 'application/json'},
                          auth=(piconf['username'], piconf['password']),
                          verify=False
                          )
        if not r.ok:
            logging.error(r.text)
