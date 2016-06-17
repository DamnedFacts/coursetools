#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys

from config import config

"""
import logging
# these two lines enable httplib debugging (requests->urllib3->httplib)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with
# HEADERS but without DATA. the only thing missing will be the response.body
# which is not logged.

import httplib
httplib.HTTPConnection.debuglevel = 1
logging.basicConfig() # you need to initialize logging, otherwise you will
                      # not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""


class InstructorAccess:
    def __init__(self):
        self.session = requests.Session()

    def login(self):
        requests.utils.add_dict_to_cookiejar(self.session.cookies, {})

        # Should obtain (mostly?) necessary cookies:
        #    JSESSIONID, _utma, _utmc, _utmz, _ga,
        #    _brand, s_session_id, session_id
        self.session.get(config['roster']['landing_url'])

        # Form data
        payload = {
            "user_id": config['roster']['user'],
            "password": config['roster']['passwd'],
            "login": "Login",
            "action": "login",
            "remote-user": "",
            "new_loc": "",
            "auth_type": "",
            "one_time_token": "",
            "encoded_pw": config['roster']['encoded_pw'],
            "encoded_pw_unicode": config['roster']['encoded_pw_unicode'],
        }

        headers = {}

        # Session metadata from visiting this URL
        self.session.post(config['roster']['login_url'],
                          data=payload,
                          headers=headers)

        # Session metadata needed viewing Instructor Access, part 1
        response = self.session.get(config['roster']['access_base_url'])

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        return response

    def logout(self):
        response = self.session.get(config['roster']['logout_url'])
        return response

    """Query Instructor Access for the student roster

    Retrieves and returns the roster of a CRN for a particular
    term. If querying a parent course, the returned dictionary includes
    multiple keys for each course CRN, with values containing the student
    roster for each.
    """
    def roster_query(self, term, crn):
        import datetime
        today = datetime.datetime.now()

        term = term.replace("_", " ").split()[0] + ' Semester'

        payload = dict(
            rosterType=2,
            rosterMonth=today.month,
            rosterDay=today.day,
            rosterYear=2015,
            rosterLoc="screen",
            CRN=crn,
            semester=term,
            year=20152016,
            rosterEmail="nobody",
            r=713
        )

        # With three key URLs visited, in login(), we can now query.
        response = self.session.get(config['roster']['access_roster_url'],
                                    params=payload)

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        roster_records = self._roster_parse(response)
        return roster_records

    def _roster_parse(self, roster_page):
        soup = BeautifulSoup(roster_page.text, "html.parser")
        roster_tables = soup.find_all("table",
                                      {"class": "rosterStudentDisplay"})
        roster_headers = soup.find_all("table",
                                       {"class": "rosterHeaderDisplay"})
        rosters = zip(roster_headers, roster_tables)

        if not roster_tables:
            print("Roster error: retrieval returned 'None' as a response.")
            sys.exit(1)

        records_dict = {}

        for header, roster in rosters:
            records = {}  # store all of the records in this list
            rows = roster.find_all('tr')
            for row in rows:
                col = row.find_all('td')
                if not col:
                    continue

                stud_id = col[1].contents[0]

                a_student = dict(
                    name=col[0].contents[0],
                    email=col[0].a.contents[0],
                    stud_id=col[1].contents[0],
                    college=col[2].contents[0],
                    class_year=col[3].contents[0],
                    major=col[4].contents[0],
                    deg=col[5].contents[0],
                    hrs=col[6].contents[0].strip(),
                    grade=col[7].contents[0],
                    status=col[8].contents[0],
                    update=col[8].contents[2],
                )

                records[stud_id] = a_student

            crn = int(header.find_all('td')[5].text)
            records_dict[crn] = records

        return records_dict

    """Query Instructor Access for the list of terms

    Retrieves and returns the academic term history for the logged in
    instructor.
    """
    def term_query(self):
        response = self.session.get(config['roster']['access_terms_url'])

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        term_records = self._term_parse(response)
        return term_records

    def _term_parse(self, term_page):
        soup = BeautifulSoup(term_page.text, "html.parser")
        term_options = soup.find_all("option")

        if not term_options:
            print("Term error: retrieval returned 'None' as a response.")
            sys.exit(1)

        records = []

        for term in term_options:
            if term['value']:
                records.append(term['value'])

        return records

    """Query Instructor Access for the list of courses for a term

    Retrieves and returns the list of courses associate with an academic term
    for the logged in instructor.

    The returned dictionary of dictionaries is keyed for the parent courses,
    any child courses cross-listed with the parent courses are embedded in each
    value of the returned dictionary with a key 'crn_child'.
    """
    def course_query(self, term):
        # Session metadata needed viewing Instructor Access, part 2
        term = term.replace("_", " ")
        response = self.session.get(config['roster']['access_courses_url']
                                    + term)

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        course_records = self._course_parse(response)
        return course_records

    def _course_parse(self, course_page):
        soup = BeautifulSoup(course_page.text, "html.parser")
        course_table = soup.find("table", {"class": "courseDisplay"})

        if not course_table:
            print("Course error: retrieval returned 'None' as a response.")
            sys.exit(1)

        records = {}
        crn_parent = None

        rows = course_table.find_all('tr')

        for row in rows:
            col = row.find_all('td')
            if not col:
                continue

            crn = int(col[0].a.text)
            course = dict(
                crn=crn,
                course=col[1].text,
                course_title=col[2].a.text if col[2].a else col[2].text,
                days=col[3].text,
                time=col[4].text,
                bldg=col[5].text,
                room=col[6].text,
                enrolled=int(col[7].text) if col[7].text.isdigit() else 0,
                cap=int(col[8].text) if col[8].text.isdigit() else 0,
                cls_enrol=int(col[10].text) if col[10].text.isdigit() else 0,
                cls_cap=int(col[11].text) if col[11].text.isdigit() else 0
            )

            # If parent course
            rel = col[9].text
            if rel == 'P':
                course['crn_child'] = {}
                crn_parent = crn
            elif rel == 'C':
                if crn_parent > 0:
                    records[crn_parent]['crn_child'][crn] = (course)
                continue
            elif rel == '':
                crn_parent = None

            records[crn] = course

        return records

    def child_query(self, term, crn):
        courses = self.course_query(term)
        return courses[crn].get('crn_child', {})

    def permission_code_query(self, term):
        # Session metadata needed viewing Instructor Access, part 2
        response = self.session.get(config['roster']['access_courses_url']
                                    + term.replace("_", " "))

        if response.status_code != 200:
            raise(ConnectionError, "Received a HTTP status code of {}"
                  .format(response.status_code))

        permission_code = self._permission_code_parse(response, term)
        return permission_code

    def _permission_code_parse(self, course_page, term):
        soup = BeautifulSoup(course_page.text, "html.parser")
        permisson_code_p = soup.select("#sem{0} td p".format(term))
        import re
        pattern = re.compile(r"My Web Registration Permission Code: (1246)")
        m = pattern.search(permisson_code_p[0].text)

        if not permisson_code_p:
            print("Course error: Permission code retrieval returned 'None' "
                  "as a response.")
            sys.exit(1)

        return m.group(1)
