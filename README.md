# PimaticAutoCreateRules
AST, 12/2019

Automatically create "NotUpdated" rules in Pimatic.  
Use the Pimatic API to retrieve the list of devices and attributes and automatically create rules "was not updated" like

> Temperatur of wemosd1_og2_treppe was not updated for 24 hours



## Introduction

Creating rules can be tedious. Creating lots of identical rules for "was not updated" can get  really exhausting for lots of devices.

This Python program does this job for you.



## Prerequisites
* Python 3.6+
* Pimatic (tested with v0.9.48)
  * An authorized Pimatic user (e.g., admin user)


## How-To
1. Setup requirements
   * `pip3 install -r requirements.txt`
2. Setup local configuration file, see template `config_local.py.template`. The new name must be `config_local.py`.
3. Run `python3 step1_getattrs.py`. This creates `step1_getattrs.txt`.
4. Edit `step1_getattrs.txt` and activate rule-creation for listed items by uncommenting the lines (remove #).
5. Run `python3 step2_createrules.py`.


