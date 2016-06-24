#!/usr/bin/env python3

from courselib.blackboard import BlackBoard
import collections
from config import config
import datetime

url_base = config["registrar"]["url"] + "/labs/"
parent = "_2983819_1"
labs = {}


def fill_desc(content_id):
    tmpl_str = """<h4><span style="font-size: large;">{title}</span></h4>
<p><span style="font-size: small;">Please read the full lab description
 <a target="_blank" href={lab_url}">here</a>.</span></p><p><span
 style="font-size: small;"></span><strong><span style="font-size: small;">
The due date is {due_date}.</span></strong></p>"""

    due_date_dt = datetime.datetime.strptime(
        labs[content_id]['dueDate_datetime'],
        "%Y-%m-%d %H:%M:%S")

    due_date_str = due_date_dt.strftime("%A, %B %-d, %Y at %-I:%M:%S %p")

    return tmpl_str.format(title=labs[content_id]['__title'],
                           lab_url=labs[content_id]['__lab_url'],
                           due_date=due_date_str)
labs_list = [
    ('_436000_1', {
        '__title': "Algorithms (Group)",
        '__lab_url': url_base + "algorithms.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-23 16:30:00",
        'possible': "100",
        'isAvailable': "false",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436001_1', {
        '__title': "Object-Oriented Design (Individual)",
        '__lab_url': url_base + "object-oriented-design.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-24 23:59:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436002_1', {
        '__title': "Data Collections (Individual)",
        '__lab_url': url_base + "data-collections.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-21 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436003_1', {
        '__title': "Classes (Individual)",
        '__lab_url': url_base + "class-design.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-14 16:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436004_1', {
        '__title': "Simulation & Design (Group)",
        '__lab_url': url_base + "simulation-design.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-9 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436005_1', {
        '__title': "Loops & Booleans (Individual)",
        '__lab_url': url_base + "loops-booleans.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-7 16:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436006_1', {
        '__title': "Decision Control (Group)",
        '__lab_url': url_base + "decision-control.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-2 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436007_1', {
        '__title': "Functions (Group)",
        '__lab_url': url_base + "functions.html",
        'contentName': '',
        'dueDate_datetime': "2016-6-1 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_457841_1', {
        '__title': "Sequences, Word Count (Individual)",
        '__lab_url': url_base + "sequences-2.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-31 16:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436008_1', {
        '__title': "Sequences (Group)",
        '__lab_url': url_base + "sequences.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-26 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436009_1', {
        '__title': "Objects & Graphics (Group)",
        '__lab_url': url_base + "objects-graphics.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-25 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436010_1', {
        '__title': "Numbers (Individual)",
        '__lab_url': url_base + "numbers.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-24 16:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436011_1', {
        '__title': "Writing Programs (Group)",
        '__lab_url': url_base + "writing-programs.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-19 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
    ('_436012_1', {
        '__title': "Computers and Programs (Group)",
        '__lab_url': url_base + "computer-programs.html",
        'contentName': '',
        'dueDate_datetime': "2016-5-18 19:30:00",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }),
]
labs_list.reverse()
labs = collections.OrderedDict(labs_list)


bb = BlackBoard()
bb.login()

items = bb.list_content(parent)

for count, item in enumerate(labs.items()):
    item[1]['content_desc_text'] = fill_desc(item[0])
    item[1]['contentName'] = 'Lab Assignment #{0}'.format(count + 1)
    bb.manage_assignment(parent, item[0], list(item[1].items()))

bb.logout()
