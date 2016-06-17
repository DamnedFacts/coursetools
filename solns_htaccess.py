#!/usr/bin/env python3

import os
from config import config

output = config["solns_htaccess"]["output_file"]
output_dir = os.path.dirname(output)

if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

with open(output, "w") as f:
    htaccess_str = \
"""AuthType Basic
AuthName "CSC 161 TAs: Login with NetID"
AuthBasicProvider ldap
AuthzLDAPAuthoritative on
AuthLDAPURL "{0}'
require ldap-user {1}""".format(config["solns_htaccess"]["ldap_url"],
                                config["courselib"]["user"])

    for lab in config["admin"]["lab_TAs"].values():
        for lab_ta in lab:
            htaccess_str += " " + lab_ta['netid']

    for leader in config["admin"]["workshop_leaders"].values():
        htaccess_str += " " + leader['netid']

    print(htaccess_str, file=f)
