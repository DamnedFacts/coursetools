#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys
import re
from config import config

"""
import logging
# these two lines enable httplib debugging (requests->urllib3->httplib)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with
# HEADERS but without DATA. the only thing missing will be the response.body
# which is not logged.

import requests.packages.urllib3.connectionpool as httplib
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig() # you need to initialize logging, otherwise you will
                      # not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""


class BlackBoard:
    def __init__(self):
        self.session = requests.Session()

    def login(self):
        # Form data
        payload = {
            "user_id": config['courselib']['user'],
            "password": config['courselib']['passwd'],
            "login": "Login",
            "action": "login",
            "remote-user": "",
            "new_loc": "",
            "auth_type": "",
            "one_time_token": "",
            "encoded_pw": config['courselib']['encoded_pw'],
            "encoded_pw_unicode": config['courselib']['encoded_pw_unicode'],
        }

        # Session metadata from visiting this URL
        response = self.session.post(config['courselib']['login_url'],
                                     data=payload)

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        return response

    def logout(self):
        response = self.session.get(config['courselib']['logout_url'])
        return response

    def add_user(self, userid, role):
        courseid = config['registrar']['blackboard']['course_id']
        query = {
            "course_id": courseid,
            "contextType": "course",
            "sourceType": "COURSES",
        }
        response = self.session.get(config['courselib']['bb_edit_enroll_url'],
                                    params=query)

        soup = BeautifulSoup(response.text, "html.parser")
        nonce = soup.select('form[action="/webapps/blackboard/execute/'
                               'editCourseEnrollment"] input[name="blackboard.'
                               'platform.security.NonceUtil.nonce"]')

        if not nonce[0].attrs['value']:
            print("BlackBoard error: retrieval returned 'None' as a response.")
            sys.exit(1)

        nonce = nonce[0].attrs['value']

        payload = {
            "userName": userid,  # The user to add to the course
            "courseRoleId": role,  # Add as a Teaching Assistant
            "available": "true",  # Unsure what this does.
            "bottom_Submit": "Submit",
            "courseId": courseid,   # The BlackBoard ID for the course,
            "course_id": courseid,  # not the CRN
            "userId": "",
            "addForm": "true",
            "actionSave": "submit",
            "sourceType": "COURSES",
            "contextType": "course",
            "selectAllFromSearch": "false",
            "blackboard.platform.security.NonceUtil.nonce": nonce,
            "selectAllSearchUrl": "",
            "selectAllCount": "",
        }

        response = self.session.post(config['courselib']['bb_edit_enroll_url'],
                                     data=payload)

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.find("span", {"id": re.compile(".*Msg\d")}).text)
        return response
