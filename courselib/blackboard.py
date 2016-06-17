#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys
import re
from config import config
from pprint import pprint

"""
import logging
# these two lines enable httplib debugging (requests->urllib3->httplib)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with
# HEADERS but without DATA. the only thing missing will be the response.body
# which is not logged.

import requests.packages.urllib3.connectionpool as httplib
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig()  # you need to initialize logging, otherwise you will
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
        course_id = config['registrar']['blackboard']['course_id']
        query = {
            "course_id": course_id,
            "contextType": "course",
            "sourceType": "COURSES",
        }
        response = self.session.get(config['courselib']['bb_edit_enroll_url'],
                                    params=query)

        soup = BeautifulSoup(response.text, "lxml")
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
            "courseId": course_id,   # The BlackBoard ID for the course,
            "course_id": course_id,  # not the CRN
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

        soup = BeautifulSoup(response.text, "lxml")
        print(soup.find("span", {"id": re.compile(".*Msg\d")}).text)
        return response

    def list_content(self, content_id):
        course_id = config['registrar']['blackboard']['course_id']
        query = {
            "course_id": course_id,
            "content_id": content_id,
        }
        response = self.session.get(config['courselib']['bb_list_content_url'],
                                    params=query)

        soup = BeautifulSoup(response.text, "lxml")

        items = soup.find_all("", {"id":
                                   re.compile("contentListItem:_\d*_\d")})
        contents = {}
        for item in items:
            item_re = re.compile("contentListItem:(_\d*_\d)")
            link = item.find("a", {"href": re.compile(".*uploadAssignment.*")})
            if link:
                contents[item_re.match(item.attrs['id']).group(1)] = \
                    {'title': link.text,
                     "type": "assignment"}

        return contents

    def manage_assignment(self, parent_id, item_id, attrs):
        # We are not naming the parts of the POST request, so there is a tuple
        # with the first element as an empty string.
        for i in range(len(attrs)):
            attrs[i] = (attrs[i][0], ("", attrs[i][1]))

        print("Updating assignment id {}".format(item_id))

        payload = {
            'content_id': item_id,
            'course_id': config['registrar']['blackboard']['course_id'],
            'parent_id': parent_id,
            'method': 'showmodify',
        }

        response = self.session.get(config['courselib']
                                    ['bb_manage_assign_url'],
                                    params=payload)

        soup = BeautifulSoup(response.text, "lxml")
        form = soup.select('form#manageAssignmentForm')[0].find_all('input')

        for input_t in form:
            try:
                attrs.append((input_t['name'], ("", input_t.get('value', ""))))
            except KeyError:
                pass

        textarea = soup.select("textarea#content_desc_text")[0]
        attrs.append(("content_desc_text", ("", textarea.text)))

        # del attrs["bottom_Cancel"]
        # del attrs["bottom_Submit"]
        # del attrs["content_color_title_color"]
        # del attrs["isTracked"]
        # del attrs["limitAvailability_end_checkbox"]
        # del attrs["limitAvailability_start_checkbox"]
        # del attrs["top_Cancel"]
        # del attrs["top_Submit"]

        payload['method'] = 'modify'
        response = self.session.post(config['courselib']
                                     ['bb_manage_assign_url'],
                                     files=attrs)

        response = self.session.post('http://requestb.in/1e1nqpa1',
                                     data=payload,
                                     files=attrs)
