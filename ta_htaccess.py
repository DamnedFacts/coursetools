#!/usr/bin/env python3

import os
from config import config

output = config["ta_htaccess"]["output_file"]
output_dir = os.path.dirname(output)

if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

with open(config["ta_htaccess"]["output_file"], "w") as f:
    htaccess_str = """AuthType Basic
AuthName "CSC 161 TAs: Login with NetID"
AuthBasicProvider ldap
AuthzLDAPAuthoritative on
AuthLDAPURL "{0}"
require ldap-user {1}""".format(config["ta_htaccess"]["ldap_url"],
                                config["courselib"]["user"])

    for lab in config["admin"]["lab_TAs"].values():
        for lab_ta in lab:
            htaccess_str += " " + lab_ta['netid']

    print(htaccess_str, file=f)
