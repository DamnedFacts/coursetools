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

        # Load the course data for the course id listed in config.yaml.
        self.load_course_data()

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

    def load_course_data(self):
        import json

        payload = {
            'course_id': config['registrar']['blackboard']['course_id'],
        }
        response = self.session.get(config['courselib']['bb_jsondata_url'],
                                    params=payload)
        self.course_data = json.loads(response.text)

    def gradebook_query(self, name_or_id):
        """
        Queries gradebook data from loaded course data
        """
        try:
            int(name_or_id.replace("_", ""))

            return next((item for item in self.course_data['colDefs']
                         if item['id'] == name_or_id), None)
        except ValueError:
            return next((item for item in self.course_data['colDefs']
                         if item['name'] == name_or_id), None)

    def download_assignment(self, assign_id_or_name, all_select=False,
                            all_attempts=False):
        """
        Attributes for this action are:

        blackboard.platform.security.NonceUtil.nonce
        outcome_definition_id
        course_id
        gradebook2Return
        receiptUrl
        cmd
        top_Submit
        selectAll
        selectAllFromList
        students_to_export
        needs_grading_<STUDENT_BB_ID>
        numResults
        fileSelectOption
        """

        assign = self.gradebook_query(assign_id_or_name)

        print("Downloading assignment {0} ({1})".format(assign['name'],
                                                        assign['id']))
        ###
        payload = {
            'outcome_definition_id': assign['id'],
            'course_id': config['registrar']['blackboard']['course_id']
        }
        response = self.session.get(config['courselib']
                                    ['bb_download_assign_url'],
                                    params=payload)

        soup = BeautifulSoup(response.text, "lxml")
        nonce = soup.select('form[action="/webapps/gradebook/do/instructor'
                            '/downloadAssignment"] input[name="blackboard.'
                            'platform.security.NonceUtil.nonce"]')

        if not nonce[0].attrs['value']:
            print("BlackBoard error: retrieval returned 'None' as a response.")
            sys.exit(1)

        nonce = nonce[0].attrs['value']

        ###
        # TODO: Handle per-student download, instead of all.
        ###
        student_list = []
        for item in self.course_data['rows']:
            for student in item:
                if 'uid' in student:
                        student_list.append(("students_to_export",
                                             "_" + student['uid'] + "_1"))

        payload = {
            'blackboard.platform.security.NonceUtil.nonce': nonce,
            'outcome_definition_id': assign['id'],
            'course_id': config['registrar']['blackboard']['course_id'],
            'gradebook2Return': "",
            'receiptUrl': "",
            'cmd': "submit",
            'top_Submit': "Submit",
            'bottom_Submit': "Submit",
            'selectAll': "",
            'selectAllFromList': 'true' if all_select else 'false',
            'numResults': "25",
            'fileSelectOption': "ALL_ATTEMPT_FILES"
                                if all_attempts else
                                "LAST_ATTEMPT_FILE",
            'students_to_export': "_282039_1",
        }

        payload = list(payload.items()) + student_list

        response = self.session.post(config['courselib']
                                     ['bb_download_assign_url'],
                                     data=payload)

        soup = BeautifulSoup(response.text, "lxml")
        download_path = soup.select('#bbNG.receiptTag.content a')[0]['href']
        download_url = config['courselib']['bb_base_url'] + download_path
        filename = download_path.split('/')[-1]

        response = self.session.get(download_url)

        with open(filename, 'wb') as download:
            for block in response.iter_content(1024):
                download.write(block)
            print("Downloading assignments from '{0}'".format(response.url))
