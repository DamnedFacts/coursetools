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
        'bin/list_wsl', 'bin/final_grader',
        'bin/gsheet_quickstart', 'bin/bb_manage_assignments',
        'bin/wsl_htaccess', 'bin/wsl_mapper',
        'bin/ta_mapper', 'bin/roster', 'bin/list_gradtas'
    ],
    install_requires=[
        'attrs==17.4.0',
        'beautifulsoup4==4.6.0',
        'bs4==0.0.1',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'icalendar==4.0.0',
        'idna==2.6',
        'lxml==4.1.1',
        'pandas==0.22.0',
        'pluggy==0.6.0',
        'py==1.5.2',
        'pytest==3.3.1',
        'python-card-me==0.9.3',
        'python-dateutil==2.6.1',
        'pytz==2017.3',
        'PyYAML==3.12',
        'requests==2.18.4',
        'six==1.11.0',
        'tox==2.9.1',
        'urllib3==1.22',
        'virtualenv==15.1.0',
        'xlrd==1.1.0'
    ],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
