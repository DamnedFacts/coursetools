import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="coursetools",
    version="0.22",
    author="Richard Emile Sarkis",
    author_email="rich@sark.is",
    description=("Toolset for managing classes on Blackboard LMS and the"
                 "Instructor Access system (Univ. of Rochester-specific"),
    license="BSD",
    keywords="course tools management blackboard",
    url="https://github.com/DamnedFacts/coursetools",
    # This would be better for bin installation:
    # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    #entry_points = {
    #    'console_scripts': ['funniest-joke=funniest.command_line:main'],
    #}
    packages=['courselib', 'tests'],
    scripts=[
        'bin/gen_ical', 'bin/bb_manage_smartviews',
        'bin/gen_vcard', 'bin/bb_access',
        'bin/bb_download_assignments', 'bin/bb_manage_project',
        'bin/bb_download_gradebook', 'bin/bb_add_assistants',
        'bin/gen_classtimes', 'bin/lectures_toc',
        'bin/bb_ls_parent', 'bin/solns_htaccess',
        'bin/list_tas', 'bin/ta_htaccess', 'bin/gen_sched',
        'bin/list_wsl', 'bin/grader',
        'bin/gsheet_quickstart', 'bin/bb_manage_assignments',
        'bin/wsl_htaccess', 'bin/wsl_mapper',
        'bin/ta_mapper', 'bin/roster', 'bin/list_gradtas'
    ],
    install_requires=[
        'attrs',
        'beautifulsoup4',
        'bs4',
        'certifi',
        'chardet',
        'icalendar',
        'idna',
        'lxml',
        'pandas',
        'pluggy',
        'py',
        'pytest',
        'python-card-me',
        'python-dateutil',
        'pytz',
        'PyYAML',
        'requests',
        'six',
        'tox',
        'urllib3',
        'virtualenv',
        'xlrd'
    ],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
