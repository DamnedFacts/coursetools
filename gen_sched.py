#!/usr/bin/env python3

from enum import Enum
from datetime import datetime, time, timedelta
from math import ceil
from collections import OrderedDict
import yaml
from courselib.weekday import Weekday
from courselib.instructor_access import InstructorAccess
from config import config

access = InstructorAccess()
access.login()
courses = access.course_query(config['registrar']['term'])
access.logout()

"""
The following configuration variables need to be placed in the
config.yaml.
"""
# Get workshop days of the week
ws_days = set()   # Make sure all repeats are removed

# for workshop_crn in config['registrar']['workshops']:
#     workshop_day_codes = courses[workshop_crn]['days']
#     for day in workshop_day_codes:
#         ws_days.add(Weekday(day))
ws_days = tuple({Weekday(day)
                 for workshop_crn in config['registrar']['workshops']
                 if workshop_crn in courses
                 for day in courses[workshop_crn]['days']})

session_start = config['registrar']['session_start']
session_end = config['registrar']['session_end']
breaks = config['gen_sched']['breaks']

workshop_day = Weekday.Sunday\
    if not ws_days or Weekday.Sunday in ws_days and min(ws_days) == 0\
    else min(ws_days)

# Multiple topics per lecture can be placed in a tuple.
topics = tuple([topic['title'] for topic in config['gen_sched']['topics']
                for t in range(topic['lectures'])])

workshops = tuple([topic['title'] for topic in config['gen_sched']['topics']
                   if topic['graded']])
quizzes = workshops
labs = workshops

exams = config['gen_sched']['exams']
misc = config['gen_sched']['misc']

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
states = []

dump_dict = OrderedDict()


def dump_agenda(label, day, title, desc):
    if day:
        dump_dict[label] = (datetime.combine(day, time(23, 59)), title, desc)
    else:
        dump_dict[label] = (title, desc)


def print_agenda(day, agenda):
    if __name__ != '__main__':
        return

    if day:
        print(day.strftime(",\"%a, %b %-d %Y\",\"{0}\"".format(agenda)),
              file=sched_fh)
    else:
        print(agenda, file=sched_fh)


def is_topic(topic):
    for t in topics:
        if type(t) == tuple and topic in t:
            return t
        if (t and t[0] == "+" and t[1:] == topic) or t == topic:
            return t

    return False


def gen_misc(day, class_state):
    #
    # Miscellaneous Items
    # This is first because these items are likely needed to be
    # scheduled directly and without regard to scheduling dependencies
    # created below.
    if misc.get(day):
        print_agenda(day, "{0}".format(misc[day][0]))


def gen_breaks(day, class_state):
    #
    # Academic breaks
    #
    break_name, break_dates = class_state.is_break()
    if break_name:
        # If the current incremented date falls within a break period
        print_agenda(day, "*{0}*".format(break_name))
        break_len = (break_dates['end'] - break_dates['start']).days + 1
        return break_name, break_dates, break_len

    return break_name, break_dates, None


def gen_exams(day, break_name, class_state):
    #
    # Exams:
    #
    if exams.get(day) and not break_name:
        print_agenda(day, "Exam: {0}".format(exams[day][0]))


def gen_lectures(day, weekday, lecture_num, break_name, break_dates,
                 break_len, topic_num, class_state):
    #
    # Lecture topics
    #

    if not class_state.is_classday():
        pass
    elif day in misc and misc[day][1] == 'lecture':
        pass
    elif class_state.cancel_threshold() and \
        (topics.count(topics[topic_num]) * len(config['registrar']['crn']) >=
         class_state.len()):
        print_agenda(day, "No lecture today")
    elif class_state.cancel_threshold(future=True) and \
        (topics.count(topics[topic_num]) * len(config['registrar']['crn']) >=
         class_state.len()):
        print_agenda(day, "No lecture today")
    elif exams.get(day, (False, False))[1]:
        class_state.cancelled()
    elif exams.get(day - timedelta(days=1), (False, False))[1]:
        print_agenda(day, "No lecture today")
        class_state.cancelled()
    elif exams.get(day + timedelta(days=1), (False, False))[1]:
        print_agenda(day, "No lecture today")
        class_state.cancelled()
    elif break_name:
        class_state.cancelled()
    elif not break_name:
        class_state.set_finished()
        class_state.set_topic(topics[lecture_num])
        section = class_state.section()

        if isinstance(topics[lecture_num], tuple):
            agenda = "**Lecture {0} ** *({1} section)*: {2}".format(", ".join(
                [str(x) for x in range(topic_num + 1, topic_num + 1 +
                                       len(topics[lecture_num]))]),
                section, ", ".join(topics[lecture_num]))

            try:
                if topics[lecture_num] != topics[lecture_num +
                                                 len(topics[lecture_num])]:
                    topic_num += len(topics[lecture_num])
            except IndexError:
                topic_num += len(topics)
        elif topics[lecture_num] not in workshops:
            agenda = "**Lecture** *({0} section)*: {1}".format(
                section,
                topics[lecture_num])
        else:
            agenda = "**Lecture {0}** *({1} section)*: {2}".format(
                topic_num + 1,
                section,
                topics[lecture_num])

            if class_state.group_finished() and \
                    topics[lecture_num] != topics[lecture_num + 1]:
                class_state.topic_inc()
                topic_num += 1

        print_agenda(day, agenda)
        if class_state.group_finished():
            lecture_num += 1

    return lecture_num, topic_num


def gen_workshop(day, weekday, break_name, break_len, workshop_num,
                 class_state):
    #
    # Workshop Cycles
    #
    if not ws_days:
        pass
    elif week == 1 and day == session_start:
        print_agenda(day, "No workshop cycle this week")
    elif weekday != workshop_day:
        pass
    elif day in misc and misc[day][1] == 'Workshop':
        pass
    elif class_state.cancel_threshold() and\
            topics.count(topics[topic_num]) >= class_state.len():
        print_agenda(day, "No workshop cycle this week")
    elif (day + timedelta(days=len(ws_days))) > session_end:
        print_agenda(day, "No workshop cycle this week")
    elif class_state.cancel_threshold(future=True) and \
        (topics.count(topics[topic_num]) * len(config['registrar']['crn']) >=
         class_state.len()):
        print_agenda(day, "No workshop cycle this week")
    elif ((break_name and break_len > (round(len(ws_days)*0.3))) or
          (topics[lecture_num] not in workshops or
           topics[lecture_num + 1] not in workshops) or
          is_topic(workshops[workshop_num]) == topics[lecture_num]):
        print_agenda(day, "No workshop cycle this week")
    elif week < final_week and is_topic(workshops[workshop_num]):
        agenda = "Workshop Cycle "
        t_list = []
        w_num = workshop_num

        if class_state.week_finished():
            _class_state = class_state
        else:
            _class_state = states[-1]

        for i in range(topic_num - _class_state.topic_count(), topic_num):
            t_list.append("{0}".format(w_num + 1))
            w_num += 1
        agenda += " & ".join(t_list) + ": "

        t_list.clear()
        for i in range(topic_num - _class_state.topic_count(), topic_num):
            t_list.append("{0}".format(workshops[workshop_num]))
            workshop_num += 1
        agenda += ", ".join(t_list)
        print_agenda(day, agenda)

    return workshop_num

def states_recent_topic():
    for i in range(len(states) - 1, -1, -1):
        if not states[i].get_topics():
            continue
        return states[i].get_topics()[-1]
    return None

def gen_quizzes(day, weekday, break_name, break_len, quiz_num,
                class_state):
    """
    Quizzes
    """
    if not class_state.is_classday() or \
            weekday != max(class_state.section_enum()):
        pass
    elif (break_name and break_len > (round(len(ws_days)*0.3))):
        print_agenda(day, "No quiz this week")
    elif states_recent_topic() not in quizzes:
        print_agenda(day, "No quiz this week")
    elif class_state.cancel_threshold() and\
            topics.count(topics[topic_num]) >= class_state.len():
        print_agenda(day, "No quiz this week")
    elif week > 1 and week < final_week and states[-1].section_finished():
        print_agenda(day, "Quiz {0} *({1} section)*: {2}"
                     .format(quiz_num + 1,
                             class_state.section(),
                             quizzes[quiz_num]))

        if class_state.week_finished():
            quiz_num += 1

    return quiz_num


def gen_projects(day, weekday, break_name, break_len, quiz_num,
                class_state):
    """
    Projects and their milestones

    Rules:
        Projects start after midterms, week # or topic?
    """
    pass


def gen_labs(day, weekday, break_dates, break_len, labs_num,
             class_state):
    #
    # Lab Assignments
    #
    if weekday != max(class_state.sections_enum()):
        return labs_num

    if (topics[lecture_num] not in labs or
            topics[lecture_num - 1] not in labs or
            is_topic(labs[labs_num]) == topics[lecture_num]):
        print_agenda(day, "No lab assigned this week")
    elif class_state.cancel_threshold() and\
            topics.count(topics[topic_num]) >= class_state.len():
        print_agenda(day, "No lab assigned this week")
    elif week < final_week \
        and week > 1 \
        and labs_num < len(labs) \
        and is_topic(labs[labs_num]) \
        and not (break_dates and
                 break_len > 1 and
                 break_dates['start'] <= day <= break_dates['end']):

        agenda = "Lab "
        t_list = []
        l_num = labs_num
        for i in range(topic_num - class_state.topic_count(), topic_num):
            t_list.append("{0}".format(l_num + 1))
            l_num += 1
        agenda += ", ".join(t_list) + " Assigned: "

        t_list.clear()

        for i in range(topic_num - class_state.topic_count(), topic_num):
            t_list.append("{0}".format(labs[labs_num]))
            labs_num += 1

        for i, j in enumerate(range(topic_num - class_state.topic_count(),
                                    topic_num)):
            dump_agenda("lab{0}".format(j + 1),
                        day,
                        "Lab Assignment #{0}".format(j + 1),
                        t_list[i])

        agenda += ", ".join(t_list)
        print_agenda(day, agenda)

    return labs_num


class ClassState:
    class State(Enum):
        pending = 0
        finished = 1
        cancelled = 2

    def __init__(self, session_start, session_end):
        self.session_start = session_start
        self.session_end = session_end
        # It's presumed that each section are equal in their lecture days
        self._states = []
        self.topic_increment = 0

        for crn in config['registrar']['crn']:  # Multiple section support
            self._states = self._states + [[] for _ in courses[crn]['days']]
            for idx, day in enumerate(courses[crn]['days']):
                # Reform lectures grouping not by section, but by lecture num
                # for that week.
                self._states[idx].append(
                    {"dow": Weekday(day),
                     "state": self.State.pending,
                     "topic": None
                     }
                )

    def topic_inc(self):
        self.topic_increment += 1

    def topic_count(self):
        return self.topic_increment

    def update_day(self, day):
        self.day = day

        if day < self.session_start or \
                day > self.session_end:
            self.cancelled()

    def reset_state(self):
        self.__init__(self.session_start, self.session_end)

    def cancelled(self):
        weekday = Weekday(self.day.weekday())
        for group in self._states:
            for lecture in group:
                if weekday is lecture['dow']:
                    lecture['state'] = self.State.cancelled

    def set_finished(self):
        weekday = Weekday(self.day.weekday())
        for group in self._states:
            for lecture in group:
                if weekday is lecture['dow']:
                    lecture['state'] = self.State.finished

    def set_topic(self, topic):
        weekday = Weekday(self.day.weekday())
        for group in self._states:
            for lecture in group:
                if weekday is lecture['dow']:
                    lecture['topic'] = topic

    def get_topics(self):
        topics = []
        for group in self._states:
            for lecture in group:
                if lecture['topic']:
                    topics.append(lecture['topic'])
        return topics

    def group(self):
        weekday = Weekday(self.day.weekday())
        dow = []
        in_group = False
        for group in self._states:
            if in_group:
                break

            for lecture in group:
                if lecture['dow'] is weekday:
                    in_group = True
                dow.append(weekday)
        return dow

    def section(self):
        weekday = Weekday(self.day.weekday())
        for crn in config['registrar']['crn']:  # Multiple section support
            for day in courses[crn]['days']:
                if weekday is Weekday(day):
                    return courses[crn]['days']
        return ""

    def sections(self):
        days = []
        for crn in config['registrar']['crn']:  # Multiple section support
            for day in courses[crn]['days']:
                    days.append(day)
        return days

    def sections_enum(self):
        return [Weekday(day) for day in self.sections()]

    def section_enum(self):
        return [Weekday(day) for day in self.section()]

    def section_finished(self):
        done = True
        sect = self.section_enum()

        for group in self._states:
            for lecture in group:
                if lecture['dow'] in sect and\
                        lecture['state'] is self.State.pending:
                    done = False

        return done

    def group_finished(self):
        done = True
        weekday = Weekday(self.day.weekday())

        in_group = False

        for group in self._states:
            if in_group:
                break

            for lecture in group:
                if lecture['dow'] is weekday:
                    in_group = True  # In lecture 'group'

                if in_group and lecture['state'] is self.State.pending:
                    done = False

        return done

    def week_finished(self):
        done = True

        for group in self._states:
            for lecture in group:
                if lecture['state'] is self.State.pending:
                    done = False

        return done

    def cancel_threshold(self, future=False):
        """
        Do we exceed a cancel threshold of lectures for the week?
        """
        thresh = 0.5  # 50%
        _true = 0

        if future:
            dow_t = Weekday(self.day.weekday())
            class_dow = self.sections_enum()
            i = len(class_dow)

            for dow in class_dow:
                diff = timedelta(days=dow - dow_t)
                if self.is_break(day=self.day+diff)[0]:
                    _true += 1
        else:
            for i, d in enumerate(self._states):
                for l in d:
                    if self.State.cancelled is l['state']:
                        _true += 1

                    i += 1

        return _true/i >= thresh

    def is_break(self, day=None):
        day = self.day if not day else day

        for (break_name, break_dates) in breaks.items():
            if day >= break_dates["start"] \
                    and day <= break_dates["end"]:
                return break_name, break_dates

        return None, None

    def is_classday(self):
        weekday = Weekday(self.day.weekday())
        for group in self._states:
            for lecture in group:
                if weekday is lecture['dow']:
                    return True
        return False

    def len(self):
        length = 0
        for group in self._states:
            length += len(group)
        return length


def gen_sched():
    global lecture_num, workshop_num, quiz_num, labs_num, topic_num,\
        break_bump, week, session_start

    # If our acadmic start date isn't a monday (our beginning of the week),
    # shift it to make the week-counting calculations correct.
    adj_session_start = session_start - timedelta(days=session_start.weekday())
    total_days = (session_end - adj_session_start).days + 1
    class_state = ClassState(session_start, session_end)

    for i in range(total_days):
        aday = adj_session_start + timedelta(days=i)
        week = int(i/7) + 1
        weekday = Weekday(aday.weekday())

        class_state.update_day(aday)
        #
        # Current week row header
        #
        if i % 7 == 0:
            states.append(class_state)
            class_state = ClassState(session_start, session_end)
            class_state.update_day(aday)
            print_agenda(None, "Week {0:0d},,".format(week))


        if i < session_start_weekday:
            continue

        # Miscellaneous Items
        gen_misc(aday, class_state)

        # Academic breaks
        break_name, break_dates, break_len = gen_breaks(aday, class_state)

        # Exams
        gen_exams(aday, break_name, class_state)

        # Lectures
        lecture_num, topic_num = gen_lectures(aday, weekday, lecture_num,
                                              break_name, break_dates,
                                              break_len,
                                              topic_num,
                                              class_state)

        # Workshop Cycles
        workshop_num = gen_workshop(aday, weekday, break_name,
                                    break_len, workshop_num,
                                    class_state)

        # Quizzes
        quiz_num = gen_quizzes(aday, weekday, break_name, break_len, quiz_num,
                               class_state)

        # Lab Assignments
        labs_num = gen_labs(aday, weekday, break_dates, break_len, labs_num,
                            class_state)

    with open(config['gen_sched']['yaml_output_file'], "w") as f:
        f.write(yaml.dump(dump_dict))

with open(sched_file, 'w') as sched_fh:
    gen_sched()
