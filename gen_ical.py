#!/usr/bin/env python3

from icalendar import Calendar, Event
from icalendar.prop import vRecur
from config import config
from datetime import datetime, timedelta
from courselib.weekday import Weekday
from courselib.instructor_access import InstructorAccess


def recur_adjust(start_d, end_d):
    class_days = [Weekday(d) for d in lecture['days']]

    start_dow = class_days[0]
    end_dow = class_days[-1]
    if start_d.weekday() < start_dow:
        start_d = start_d + timedelta(days=(start_dow - start_d.weekday()))

    if end_d.weekday() > end_dow:
        end_d = end_d - timedelta(days=(end_d.weekday() - end_dow - 1))

    return start_d, end_d

access = InstructorAccess()
access.login()
courses = access.course_query(config['registrar']["term"])


cal = Calendar()
cal.add('prodid', '-//My calendar product//mxm.dk//')
cal.add('version', '2.0')

#
# Lecture Event
#
lecture = courses[config['registrar']['crn']]
days = [Weekday(d).to_ical() for d in lecture['days']]
times = lecture['time'].split('-')

summary = config['registrar']['course'] + ": Lecture"
start_t = datetime.strptime(times[0], "%H%M").time()
end_t = datetime.strptime(times[1], "%H%M").time()
start_d = config['gen_sched']['session_start']
end_d = config['gen_sched']['session_end']
recur = vRecur()
recur['UNTIL'] = end_d
recur['FREQ'] = "WEEKLY"
recur['INTERVAL'] = 1
recur['BYDAY'] = days

start_d, end_d = recur_adjust(start_d, end_d)

recur['UNTIL'] = end_d

event = Event()
event.add('SUMMARY', summary)
event.add('DTSTART', datetime.combine(start_d, start_t))
event.add('DTEND', datetime.combine(start_d, end_t))
event.add('LOCATION', lecture['bldg'] + " " + lecture['room'])
event.add('URL', config['registrar']['url'])
event.add('RRULE', recur)
cal.add_component(event)

#
# Lab Events
#
for lab_crn in config['registrar']['labs']:
    if not lab_crn:
        continue

    lab = courses[lab_crn]

    days = [Weekday(d).to_ical() for d in lab['days']]
    times = lab['time'].split('-')

    summary = config['registrar']['course'] + ": Lab"
    start_t = datetime.strptime(times[0], "%H%M").time()
    end_t = datetime.strptime(times[1], "%H%M").time()
    start_d = config['gen_sched']['session_start']
    end_d = config['gen_sched']['session_end']
    recur = vRecur()
    recur['UNTIL'] = end_d
    recur['FREQ'] = "WEEKLY"
    recur['INTERVAL'] = 1
    recur['BYDAY'] = days

    start_d, end_d = recur_adjust(start_d, end_d)

    recur['UNTIL'] = end_d

    event = Event()
    event.add('SUMMARY', summary)
    event.add('DTSTART', datetime.combine(start_d, start_t))
    event.add('DTEND', datetime.combine(start_d, end_t))
    event.add('LOCATION', lab['bldg'] + " " + lab['room'])

    comment = "Lab TAs:"
    for ta in config['admin']['lab_TAs'][lab_crn]:
        comment += " " + ta['name']
    event.add('DESCRIPTION', comment)
    event.add('RRULE', recur)
    cal.add_component(event)

#
# Workshop Events
#
for ws_crn in config['registrar']['workshops']:
    if not ws_crn:
        continue

    ws = courses[ws_crn]

    days = [Weekday(d).to_ical() for d in ws['days']]
    times = ws['time'].split('-')

    summary = config['registrar']['course'] + ": Workshop"
    start_t = datetime.strptime(times[0], "%H%M").time()
    end_t = datetime.strptime(times[1], "%H%M").time()
    start_d = config['gen_sched']['session_start']
    end_d = config['gen_sched']['session_end']
    recur = vRecur()
    recur['UNTIL'] = end_d
    recur['FREQ'] = "WEEKLY"
    recur['INTERVAL'] = 1
    recur['BYDAY'] = days

    start_d, end_d = recur_adjust(start_d, end_d)

    recur['UNTIL'] = end_d

    event = Event()
    event.add('SUMMARY', summary)
    event.add('DTSTART', datetime.combine(start_d, start_t))
    event.add('DTEND', datetime.combine(start_d, end_t))
    event.add('LOCATION', ws['bldg'] + " " + ws['room'])
    event.add('DESCRIPTION',  "Workshop Leader: " +
              config['admin']['workshop_leaders'][ws_crn]['name'])
    event.add('RRULE', recur)
    cal.add_component(event)

f = open(config['gen_ical']['output_dir'] + 'csc161-cal.ics', 'wb')
f.write(cal.to_ical())
f.close()
