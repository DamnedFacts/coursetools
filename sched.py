from datetime import timedelta
import sys
from courselib.weekday import Weekday
from courselib.instructor_access import InstructorAccess
from config import config


def retrieve_term_info():
    access = InstructorAccess()
    access.login()
    courses = access.course_query(config['registrar']['term'])
    access.logout()
    return courses


def get_lecture_weekdays(courses):
    # Get lecture days of the week
    class_days = []

    # We may have multiple lecture sections
    for crn in config['registrar']['crn']:
        for day in courses[crn]['days']:
            class_days.append(Weekday(day))

    return tuple(class_days)


def get_workshop_weekdays(courses):
    # Get workshop days of the week
    # Make sure all workshops occurring on the same day are removed.
    workshop_days = set()

    if None not in config['registrar']['workshops']:
        for workshop_crn in config['registrar']['workshops']:
            for day in courses[workshop_crn]['days']:
                workshop_days.add(Weekday(day))

    return tuple(workshop_days)


# Position in list is (week # - 1)
weeks = [
]


class SchedTree:
    filial = []

    def __init__(self, name, data):
        self.children = {}
        self.data = data
        self.name = name

    def add_node(self, name, data):
        self.children[name] = SchedTree(name, data)

    def __getitem__(self, y):
        if y in self.children:
            return self.children[y]
        else:
            raise KeyError

    def get(self, y):
        if y in self.children:
            return self.children[y]
        else:
            return None

    def __str__(self, depth=0):
        ret = ""

        spacing = "       " * depth

        ret += spacing + "| " + str(self.name) + "\n"
        ret += spacing + "  " + str(self.data) + "\n"

        for child in self.children.values():
            ret += child.__str__(depth + 1)

        return ret


class Lecture:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Workshop:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Quiz:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Lab:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Exam:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Misc:
    topics = config['gen_sched']['topics']

    def __init__(self, day, topic):
        pass


class Break:
    def __init__(self, day, topic):
        pass


class Week:
    def __init__(self, week, topic):
        self.week = week

sched_tree = SchedTree(config['registrar']['title'], None)


def schedule_item(week, item):
    if type(item) == Week and not sched_tree.get(week):
        sched_tree.add_node(week, item)
        sched_tree[week].add_node('Lectures', [])
        sched_tree[week].add_node('Exam', None)
        sched_tree[week].add_node('Misc', None)
        sched_tree[week].add_node('Break', None)
    elif type(item) == Lecture:
        sched_tree[week]['Lectures'].data.append(item)
        sched_tree[week]['Lectures'].add_node('Workshop', None)
        sched_tree[week]['Lectures'].add_node('Quiz', None)
        sched_tree[week]['Lectures'].add_node('Lab', None)
    elif type(item) == Workshop:
        sched_tree[week]['Lectures']['Workshop'].data = item
    elif type(item) == Quiz:
        sched_tree[week]['Lectures']['Quiz'].data = item
    elif type(item) == Lab:
        sched_tree[week]['Lectures']['Lab'].data = item
    elif type(item) == Exam:
        sched_tree[week]['Exam'].data = item
    elif type(item) == Misc:
        sched_tree[week]['Misc'].data = item
    elif type(item) == Break:
        sched_tree[week]['Break'].data = item


def run_timeline():
    session_start = config['gen_sched']['session_start']
    session_end = config['gen_sched']['session_end']

    # Align session_start to beginning of the week.
    session_start = session_start - timedelta(days=session_start.weekday())

    # Align session_end to end of the week.
    session_end = session_end + timedelta(days=(6 - session_end.weekday()))

    # Total number of days of the semester, after alignment to a full week.
    total_days = (session_end - session_start).days + 1

    courses = retrieve_term_info()
    class_weekdays = get_lecture_weekdays(courses)
    workshop_weekdays = get_workshop_weekdays(courses)

    for i in range(total_days):
        try:
            day = session_start + timedelta(days=i)
            weekday = Weekday(day.weekday())
            week = int(i/7) + 1

            if i % 7 == 0:
                schedule_item(week, Week(week, None))

            if weekday in class_weekdays:
                schedule_item(week, Lecture(day, None))

            if weekday == min(workshop_weekdays):
                schedule_item(week, Workshop(day, None))

            if weekday == max(class_weekdays) + 1:  # Quiz
                schedule_item(week, Quiz(day, None))

            if weekday == max(class_weekdays) + 1:  # Lab
                schedule_item(week, Lab(day, None))

            if day in config['gen_sched']['exams']:
                schedule_item(week, Exam(day, None))

            if day in config['gen_sched']['misc']:
                schedule_item(week, Misc(day, None))

            if day in config['gen_sched']['breaks']:
                schedule_item(week, Break(day, None))

        except IndexError:
            print("Not enough topics to fill the schedule.")
            sys.exit(1)

    print(sched_tree)
run_timeline()
