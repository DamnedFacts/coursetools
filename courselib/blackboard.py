#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys
import re
from courselib.config import config
from courselib.utils import pretty_print_post
import json

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

    def create_smartview(self, name, desc, student_ids, category_names,
                         favorite=False):
        course_id = config['registrar']['blackboard']['course_id']
        payload = {
            'course_id': course_id,
        }
        response = self.session.get(config['courselib']
                                    ['bb_smartview_manage_url'],
                                    params=payload)

        soup = BeautifulSoup(response.text, "lxml")
        svid = list(filter(lambda x: True if x['name'] == name else False,
                           self.course_data['customViews']))

        payload = {
            'course_id': course_id,
            'actionType': 'modify',  # If no ID is supplied, creates new.
        }

        if svid:
            payload['id'] = "_" + svid[0]['id'] + "_1"

        response = self.session.get(config['courselib']
                                    ['bb_smartview_add_url'],
                                    params=payload)

        soup = BeautifulSoup(response.text, "lxml")

        nonce = soup.select('#custom_view_form '
                            'input[name="blackboard.'
                            'platform.security.NonceUtil.nonce"]')

        if not nonce or not nonce[0].attrs['value']:
            print("BlackBoard error: nonce retrieval failed.")
            sys.exit(1)

        nonce = nonce[0].attrs['value']

        payload = [
            ('blackboard.platform.security.NonceUtil.nonce', nonce),
            ('course_id', course_id),
            ('hasUserId', 'true'),
            ('favorite', 'true'),
            ('name', name),
            ('description', desc),
            ('favoriteCbox', 'true'),
            ('searchType', 'simple'),
            ('categorySel', 'all'),
            ('userSel', 'selectedUsers'),
            ('studentinclude', 'selected'),
            ('divId', '#'),
            ('fid#', '1'),
            ('queryCriteria#', '109062'),
            ('queryCondition#', 'eq'),
            ('queryTextValue#', ''),
            ('queryText2Value#', ''),
            ('queryRadioValue#', 'A'),
            ('queryDValue#', ''),
            ('count', '0'),
            ('cumulativeCount', '0'),
            ('filterQueryCriteria', 'bycat'),
            ('filterQueryCondition', '275996'),
            ('bottom_Submit', "Submit"),
        ]

        if svid:
            payload.append(('id', "_" + svid[0]['id'] + "_1"))

        cids = []
        for category in category_names:
            cid = list(filter(lambda x: True if x['name'] == category
                              else False,
                              self.course_data['categories']))

            if cid:
                cids.append(cid[0]['id'])

        students = {}
        students['userIds'] = ['st_' + self.sid_to_bbid[sid]
                               for sid in student_ids
                               if sid in self.sid_to_bbid]

        students['showstuhidden'] = False

        display = {}
        display['showhidden'] = False
        display['items'] = 'bycat'
        display['ids'] = ['c_' + str(cid) for cid in cids]
        json_text = {'searchType': 'simple'}
        json_text['students'] = students
        json_text['display'] = display
        payload.append(('jsonText', json.dumps(json_text)[1:-1]))

        aliases = {'aliases': [{'alias': 'st_' + self.sid_to_bbid[sid],
                                'id': self.sid_to_bbid[sid]}
                               for sid in student_ids
                               if sid in self.sid_to_bbid]}

        aliases['aliases'] += [{'alias': 'c_' + cid, 'id': cid}
                               for cid in cids]

        payload.append(('aliasJSonStr', json.dumps(aliases)))

        alias_string = ['st_' + self.sid_to_bbid[sid] + ":" +
                        self.sid_to_bbid[sid]
                        for sid in student_ids
                        if sid in self.sid_to_bbid]
        alias_string += ['c_' + cid + ":" + cid
                         for cid in cids]

        payload.append(('aliasString', ",".join(alias_string)))

        payload += [('simpleList', self.sid_to_bbid[sid])
                    for sid in student_ids
                    if sid in self.sid_to_bbid]

        response = self.session.post(
            config['courselib']['bb_smartview_add_url'],
            data=payload)

        soup = BeautifulSoup(response.text, 'lxml')
        if len(soup.select("span#badMsg1")) > 0:
            print(soup.select("span#badMsg1")[0].text)

    def manage_assignment(self, parent_id, item_id, attrs):
        # TODO: Should raise exception for possible issues.
        # We are not naming the parts of the POST request, so there is a tuple
        # with the first element as an empty string.
        for i in range(len(attrs)):
            attrs[i] = (attrs[i][0], (None, attrs[i][1]))

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
        form = soup.select('form#manageAssignmentFormId')[0].find_all('input')

        for input_t in form:
            try:
                attrs.append((input_t['name'], (None, input_t.get('value', ""))))
            except KeyError:
                pass

        textarea = soup.select("textarea#content_desc_text")[0]
        attrs.append(("content_desc_text", (None, textarea.text)))

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
        if response.status_code != 200:
            raise ConnectionError("Received a HTTP status code of {}"
                                  .format(response.status_code))

    def load_course_data(self):
        payload = {
            'course_id': config['registrar']['blackboard']['course_id'],
            'version':"-1"
        }

        response = self.session.get(config['courselib']['bb_jsondata_url'],
                                    params=payload)

        self.course_data = json.loads(response.text)

        if 'cachedBook' in self.course_data:
            print("Using cached course JSON data...")
            self.course_data = self.course_data['cachedBook']

        self.student_dict = {data['uid']: stud
                             for stud in self.course_data['rows']
                             for data in stud if data.get('uid')}

        self.bbid_to_sid = {data['uid']:
                            list(filter(lambda x: True
                                        if x.get('c') == 'SI'
                                        else False, stud))[0]['v']
                            for stud in self.course_data['rows']
                            for data in stud if data.get('uid')}

        self.sid_to_bbid = {data['v']:
                            list(filter(lambda x: True
                                        if x.get('uid')
                                        else False, stud))[0]['uid']
                            for stud in self.course_data['rows']
                            for data in stud if data.get('c') == 'SI'}

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

        if not assign:
            raise KeyError(f"Gradebook column '{assign_id_or_name}' not found!")

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

    def download_gradebook(self, options, output_dir=None):
        course_id = config['registrar']['blackboard']['course_id']
        payload = {
            'course_id': course_id,
            'dispatch': 'viewDownloadOptions',
        }

        response = self.session.get(config['courselib']
                                    ['bb_download_gradebook_url'],
                                    params=payload)

        soup = BeautifulSoup(response.text, "lxml")
        nonce = soup.select('form[action="/webapps/gradebook/do/instructor/'
                            'downloadGradebook"] input[name="blackboard.'
                            'platform.security.NonceUtil.nonce"]')

        if not nonce[0].attrs['value']:
            print("BlackBoard error: retrieval returned 'None' as a response.")
            sys.exit(1)

        nonce_1 = nonce[0].attrs['value']

        # Next, POST the form data, and parse the response.
        payload = {
            'course_id': course_id,
            "userIds": "",
            "itemIds": "",
            "noCustomView": "false",
            "dispatch": "setDownloadOptions",
            "downloadOption": "ALL",
            "item": course_id,
            "delimiter": "TAB",
            "hidden": "false",
            "downloadTo": "LOCAL",
            "targetPath_CSFile": "",
            "targetPath_attachmentType": "C",
            "targetPath_fileId": "",
            "bottom_Submit": "Submit",
        }

        payload = list(payload.items()) + \
            [('blackboard.platform.security.NonceUtil.nonce', nonce_1)]

        response = self.session.post(
            config['courselib']['bb_download_gradebook_url'],
            data=payload)

        # This should be the download page
        soup = BeautifulSoup(response.text, "lxml")
        css_selector = 'form[id="download_form"] '\
            'input[name='\
            '"blackboard.platform.security.NonceUtil.nonce"]'
        nonce = soup.select(css_selector)

        if not nonce[0].attrs['value']:
            print("BlackBoard error: retrieval returned 'None' as a response.")
            sys.exit(1)

        nonce = nonce[0].attrs['value']

        payload = {
            "course_id": course_id,
            "downloadOption": "ALL",
            "delimiter": "TAB",
            "item": course_id,
            "gradePeriod": "",
            "comments": "false",
            "hidden": "false",
            "userIds": "",
            "itemIds": "",
            "downloadTo": "LOCAL",
            "blackboard.platform.security.NonceUtil.nonce": nonce,
        }

        # Download the gradebook
        download_url = config['courselib']['bb_download_gradebook_url'] + \
            "dispatch=executeDownload"

        response = self.session.post(download_url, data=payload)

        import re
        pattern = re.compile(';\s?filename="(.*)"\s*;')
        header = response.headers['Content-Disposition']
        filename = pattern.findall(header)[0]

        if output_dir:
            filename = output_dir + filename

        with open(filename, 'wb') as download:
            for block in response.iter_content(1024):
                download.write(block)
            print("Downloading gradebook...")
