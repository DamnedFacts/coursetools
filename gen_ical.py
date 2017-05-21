#!/usr/bin/env python3

from icalendar import Calendar, Event
from icalendar.prop import vRecur
from config import config
from datetime import datetime, timedelta
from courselib.weekday import Weekday
from courselib.instructor_access import InstructorAccess


def recur_adjust(days):
    sess_start = config['registrar']['session_start']
    sess_end = config['registrar']['session_end']

    start_d = sess_start
    end_d = sess_end

    days = [Weekday(d) for d in days]
    start_dow = days[0]
    end_dow = days[-1]

    if len(days) == 1:
        if start_dow < sess_start.weekday():
            start_d = sess_start + timedelta(days=(start_dow -
                                                   sess_start.weekday() + 7))

        if end_dow > sess_end.weekday():
            end_d = sess_end - timedelta(days=(sess_end.weekday() -
                                               end_dow - 7))
    elif len(days) > 1:
        for day in days:
            if day > sess_start.weekday():
                start_d = sess_start + timedelta(days=(day -
                                                       sess_start.weekday()))
                break

        for day in days:
            if day < sess_end.weekday():
                end_d = sess_end - timedelta(days=(sess_end.weekday() - day))
                break

    return start_d, end_d

access = InstructorAccess()
access.login()
courses = access.course_query(config['registrar']["term"])


cal = Calendar()
cal.add('prodid', '-//CSC 161 Calendar//mxm.dk//')
cal.add('version', '2.0')

#
# Lecture Event
#
for lecture_crn in config['registrar']['crn']:
    lecture = courses[lecture_crn]
    days = [Weekday(d).to_ical() for d in lecture['days']]
    times = lecture['time'].split('-')

    summary = config['registrar']['course'] + ": Lecture"
    start_t = datetime.strptime(times[0], "%H%M").time()
    end_t = datetime.strptime(times[1], "%H%M").time()

    start_d, end_d = recur_adjust(days)

    recur = vRecur()
    recur['UNTIL'] = end_d
    recur['FREQ'] = "WEEKLY"
    recur['INTERVAL'] = 1
    recur['BYDAY'] = days

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

    if lab_crn not in courses:
        print("Lab session CRN {0} not found. Skipping…"
              .format(lab_crn))
        continue

    lab = courses[lab_crn]

    days = [Weekday(d).to_ical() for d in lab['days']]
    times = lab['time'].split('-')

    summary = config['registrar']['course'] + ": Lab"
    start_t = datetime.strptime(times[0], "%H%M").time()
    end_t = datetime.strptime(times[1], "%H%M").time()

    start_d, end_d = recur_adjust(days)

    recur = vRecur()
    recur['UNTIL'] = end_d
    recur['FREQ'] = "WEEKLY"
    recur['INTERVAL'] = 1
    recur['BYDAY'] = days

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

    if ws_crn not in courses:
        print("Workshop CRN {0} not found. Skipping…".format(ws_crn))
        continue

    ws = courses[ws_crn]

    days = [Weekday(d).to_ical() for d in ws['days']]
    times = ws['time'].split('-')

    summary = config['registrar']['course'] + ": Workshop"
    start_t = datetime.strptime(times[0], "%H%M").time()
    end_t = datetime.strptime(times[1], "%H%M").time()

    start_d, end_d = recur_adjust(days)

    recur = vRecur()
    recur['FREQ'] = "WEEKLY"
    recur['INTERVAL'] = 1
    recur['BYDAY'] = days
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
