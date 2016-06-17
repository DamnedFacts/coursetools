#!/usr/bin/env python3

from datetime import date, timedelta
from courselib.weekday import Weekday
from courselib.instructor_access import InstructorAccess
from math import ceil
from config import config

access = InstructorAccess()
access.login()

courses = access.course_query(config['registrar']['term'])

# Get lecture days of the week
lecture_day_codes = courses[config['registrar']['crn']]['days']
class_days = []
for day in lecture_day_codes:
    class_days.append(Weekday(day))
class_days.sort()

# Get workshop days of the week
workshop_days = set()   # Make sure all repeats are removed

if None not in config['registrar']['workshops']:
    for workshop_crn in config['registrar']['workshops']:
        workshop_day_codes = courses[workshop_crn]['days']
        for day in workshop_day_codes:
            workshop_days.add(Weekday(day))

access.logout()

# TODO: The following configuration variables need to be placed in the
# config.yaml.
session_start = config['gen_sched']['session_start']
session_end = config['gen_sched']['session_end']

breaks = {"Break: Martin Luther"
          " King Day": {"start": date(2016, 1, 18),
                        "end": date(2016, 1, 18)},
          "Break: Spring Break": {"start": date(2016, 3, 5),
                                  "end": date(2016, 3, 13)},
          }


class_days = tuple(class_days)
workshop_days = tuple(workshop_days)
workshop_day = Weekday.NoneDay
quiz_day = workshop_day
lab_day = Weekday.NoneDay

topics = (
    ("Introduction", "Computer Programs"),
    "Writing Programs",
    "Numbers",
    "Objects & Graphics",
    "Sequences",
    "Sequences",
    "Functions",
    "Decision Control",
    "Loops & Booleans",
    "Simulation & Design",
    "Simulation & Design",
    "Defining Classes",
    "Defining Classes",
    "Data Collections",
    "Object-Orientation",
    "Object-Orientation",
    "Algorithms",
    ("Algorithms", "Course Review"),
)

workshops = (
    "Computer Programs",
    "Writing Programs",
    "Numbers",
    "Objects & Graphics",
    "Sequences",
    "Functions",
    "Decision Control",
    "Loops & Booleans",
    "Simulation & Design",
    "Defining Classes",
    "Data Collections",
    "Object-Orientation",
    "Algorithms",
)
quizzes = workshops
labs = workshops

exams = {
    date(2016, 3, 2): ("In-Lab Midterm Exams", False),
    date(2016, 3, 3): ("In-Lab Midterm Exams", False),
    date(2016, 4, 25): ("In-Lab Final Exams", False),
    date(2016, 4, 26): ("In-Lab Final Exams", False),
}

misc = {
    date(2016, 2, 29): ("Workshop Cycle X: Midterm Review", "Workshop"),
    date(2016, 3, 18): ("Project: Milestone 1, Assigned", None),
    date(2016, 4, 1): ("Project: Milestone 2, Assigned", None),
    date(2016, 4, 15): ("Project: Milestone 3, Assigned", None),
    date(2016, 4, 26): ("**Lecture Cancelled!**", "Lecture"),
    date(2016, 4, 27): ("Last Day of Classes", None)
}

sched_file = config['gen_sched']['output_file']
# TODO: The preceding configuration variables need to be placed in the
# config.yaml.

#
# The following configurations below should not need to be changed.
#
session_start_weekday = session_start.weekday()
first_week = session_start - timedelta(days=(session_start_weekday))
final_week = ceil((session_end - first_week).days/7)
week = 0
lecture_num = 0
topic_num = 0
workshop_num = 0
quiz_num = 0
labs_num = 0
break_bump = False

sched_fh = None


def print_agenda(date, agenda):
    if date:
        print(date.strftime(",\"%a, %b %-d %Y\",\"{0}\"".format(agenda)),
              file=sched_fh)
    else:
        print(agenda, file=sched_fh)


def is_topic(topic):
    for t in topics:
        if (t and t[0] == "+" and t[1:] == topic) \
                or t == topic:
            return t

    return False


def is_break(date):
    for (break_name, break_dates) in breaks.items():
        if (date >= break_dates["start"] and date <= break_dates["end"]):
            return break_name, break_dates
    return None, None


def gen_sched():
    global lecture_num, workshop_num, quiz_num, labs_num, topic_num,\
        break_bump, week, session_start

    # If our acadmic start date isn't a monday (our beginning of the week),
    # shift it to make the week-counting calculations correct.
    session_start = session_start - timedelta(days=session_start.weekday())
    total_days = (session_end - session_start).days + 1

    for i in range(total_days):
        date = session_start + timedelta(days=i)
        week = int(i/7) + 1
        weekday = Weekday(date.weekday())

        #
        # Current week header
        #
        if i % 7 == 0:
            print_agenda(None, "Week {0:0d},,".format(week))

        if i < session_start_weekday:
            continue

        #
        # Miscellaneous Items
        # This is first because these items are likely needed to be
        # scheduled directly and without regard to scheduling dependencies
        # created below.
        if misc.get(date):
            print_agenda(date, "{0}".format(misc[date][0]))

        #
        # Academic breaks
        #
        break_name, break_dates = is_break(date)
        if break_name:
            # If the current incremented date falls within a break period
            print_agenda(date, "*{0}*".format(break_name))
            break_len = (break_dates['end'] - break_dates['start']).days + 1

        #
        # Exams:
        #
        if exams.get(date) and not break_name:
            print_agenda(date, "Exam: {0}".format(exams[date][0]))

        #
        # Lecture topics
        #
        if date in misc and misc[date][1] == 'Lecture':
            continue
        elif weekday in class_days and exams.get(date) and exams[date][1]:
            lecture_num += 1
        elif weekday in class_days and not break_name:
            if isinstance(topics[lecture_num], tuple):
                agenda = "**Lecture {0}**: {1}"\
                    .format(", ".join([str(x)
                                      for x in
                                       range(topic_num + 1,
                                             topic_num + 1 +
                                             len(topics[lecture_num]))]),
                            ", ".join(topics[lecture_num]))

                try:
                    if topics[lecture_num] != topics[lecture_num +
                                                     len(topics[lecture_num])]:
                        topic_num += len(topics[lecture_num])
                except IndexError:
                    topic_num += len(topics)
            elif topics[lecture_num] not in workshops:
                agenda = "**Lecture**: {0}".format(topics[lecture_num])
            else:
                agenda = "**Lecture {0}**: {1}".format(topic_num + 1,
                                                       topics[lecture_num])

                if topics[lecture_num] != topics[lecture_num + 1]:
                    topic_num += 1

            print_agenda(date, agenda)
            lecture_num += 1

        #
        # Workshop Cycles
        #
        if date in misc and misc[date][1] == 'Workshop':
            continue
        elif weekday == workshop_day \
                and ((break_name
                      and break_len > (round(len(workshop_days)*0.3)))
                     or (topics[lecture_num] not in workshops
                         or topics[lecture_num + 1] not in workshops)):
            print_agenda(date, "No workshop cycle this week")
        elif weekday == workshop_day \
                and week < final_week \
                and is_topic(workshops[workshop_num]):

            print_agenda(date, "Workshop Cycle {0}: {1}"
                         .format(workshop_num + 1,
                                 workshops[workshop_num]))
            workshop_num += 1

        #
        # Quizzes
        #
        if weekday == quiz_day \
                and ((break_name
                      and break_len > (round(len(workshop_days)*0.3)))
                     or (topics[lecture_num] not in quizzes
                         or topics[lecture_num + 1] not in quizzes)):
            pass
        elif weekday == quiz_day \
                and week > 2 \
                and week < final_week \
                and not exams.get(date):

            print_agenda(date, "Quiz {0} *(in workshop)*: {1}".format(
                quiz_num + 1,
                quizzes[quiz_num]))
            quiz_num += 1

        #
        # Lab Assignments
        #
        if weekday == lab_day \
                and (topics[lecture_num - 1] not in labs
                     or topics[lecture_num - 2] not in labs):
            pass
        elif weekday == lab_day \
                and week < final_week \
                and week > 1 \
                and is_topic(labs[labs_num]) \
                and not (break_dates and
                         (break_dates['end'] - break_dates['start']).days > 1
                         and
                         break_dates['start'] <= date <= break_dates['end']):

            print_agenda(date, "Lab {0} Assigned: {1}"
                         .format(labs_num + 1, labs[labs_num]))
            labs_num += 1

            try:
                if lab_day >= class_days[-1] \
                        and (labs[labs_num] == topics[lecture_num - 2]
                             or labs[labs_num] == topics[lecture_num - 1]):
                    print_agenda(date, "Lab {0} Assigned: {1}"
                                 .format(labs_num + 1, labs[labs_num]))
                    labs_num += 1
            except IndexError:
                pass


with open(sched_file, 'w') as sched_fh:
    gen_sched()
