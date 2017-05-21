#!/usr/bin/env python3

from courselib.blackboard import BlackBoard
from config import config
import datetime
import re
from config import config

url_base = config["registrar"]["url"] + "/labs/"
labs = {}


def fill_desc(assignment):
    tmpl_str = """<h4><span style="font-size: large;">{title}</span></h4>
<p><span style="font-size: small;">Please read the full lab description
 <a target="_blank" href={lab_url}>here</a>.</span></p><p><span
 style="font-size: small;"></span><strong><span style="font-size: small;">
The due date is {due_date}.</span></strong></p>"""

    due_date_dt = datetime.datetime.strptime(assignment['dueDate_datetime'],
                                             "%Y-%m-%d %H:%M:%S")

    due_date_str = due_date_dt.strftime("%A, %B %-d, %Y at %-I:%M:%S %p")

    return tmpl_str.format(title=assignment['__title'],
                           lab_url=assignment['__url'],
                           due_date=due_date_str)


bb = BlackBoard()
bb.login()

parent = config['bb_manage']['labs_parent_id']
bb_items = bb.list_content(parent)

for label, item in config['admin']['due_dates'].items():
    assign = {
        '__title': "",
        '__url': url_base + "computer-programs.html",
        'contentName': "",
        'dueDate_datetime': "",
        'possible': "100",
        'isAvailable': "true",
        'attemptType': "UNLIMITED_ATTEMPTS",
        'content_desc_text': "",
    }
    dd = item[0] + datetime.timedelta(days=7)

    url = ''.join(ch for ch in item[2].lower()
                  if ch.isalnum() or ch.isspace()).replace(" ", "-")
    url = re.sub(r'(-)\1{1,}', r'\1', url)

    assign['__title'] = item[2]
    assign['__url'] = url_base + url + ".html"
    assign['contentName'] = item[1]
    assign['dueDate_datetime'] = str(dd)
    assign['content_desc_text'] = fill_desc(assign)
    item_id = [_id for _id, val in bb_items.items() if val['title'] == item[1]]

    if not item_id:
        print("No Blackboard item for assignment {0}".format(item[2]))
        continue

    bb.manage_assignment(parent, item_id[0], list(assign.items()))

bb.logout()
