import json
import traceback
import sys
import csv
import os
import sqlite3

from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'evals.db')

NOPREF_STR = 'No preference'
RES_DIR = os.path.join(os.path.dirname(__file__), '..', 'res')
COLUMN_NAMES = dict(
    dept='Department',
    course_num='Course',
    instr='Instructor',
)

def _load_column(filename, col=0):
    """Load single column from csv file."""
    with open(filename) as f:
        col = list(zip(*csv.reader(f)))[0]
        return list(col)


def _load_res_column(filename, col=0):
    """Load column from resource directory."""
    return _load_column(os.path.join(RES_DIR, filename), col=col)


def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]


DEPTS = _build_dropdown([None] + _load_res_column('dept_list.csv'))


class SearchForm(forms.Form):
    professor = forms.CharField(
        label='Instructor name',
        help_text='e.g. "Matthew Wachs"',
        required=False)
    dept = forms.ChoiceField(
        label='Department', 
        choices=DEPTS, 
        required=False)
    course_num = forms.IntegerField(
        label='Course Number',
        help_text='e.g. "12200"',
        required=True)
    quarter = forms.CharField(
        label='Quarter',
        help_text='e.g. "Autumn"',
        required=True)
    year = forms.IntegerField(
        label='Year',
        help_text='e.g. "2018"',
        required=True)


def home(request):

    return render(request, "searcher/home.html")


def find_syllabi_and_evals(args_from_ui):
    '''
    Find information from syllabi AND evals, if available.

    Inputs:
        args_from_ui: A dictionary of arguments from the UI to query.

    Output:
        a sql query result.
    '''
    
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()

    extra = "GROUP BY professor;"
    args_list = []
    args_list.append(args_from_ui['dept'])
    args_list.append(args_from_ui['course_num'])
    args_list.append(args_from_ui['year'])
    args_list.append(args_from_ui['quarter'])
    if 'professor' in args_from_ui:
        cleaned = " ".join(args_from_ui['professor'].split())
        cleaned = cleaned.upper()
        args_list.append(cleaned)
        extra = " AND professor = ? GROUP BY professor;"


    query = ('SELECT dept, course_num, title, professor, prof_sentiment, ' 
    'course_sentiment, num_due, grade_breakdown,' 
    ' ROUND(office_hours * 1.0 / enrollment, 2) AS hrs_per_student, by_appointment '
    'FROM courses JOIN instructor_sentiment JOIN class_sentiment ' 
    'JOIN overview JOIN days_off ON '
    'courses.course_id = instructor_sentiment.course_id ' 
    'AND instructor_sentiment.course_id = class_sentiment.course_id AND ' 
    'class_sentiment.course_id = overview.course_id AND ' 
    'overview.course_id = days_off.course_id '
    'WHERE dept = ? AND '
    'course_num = ? AND overview.year = ? AND overview.quarter = ?')
    query += extra

    course_titles = c.execute(query, args_list)

    return (get_header(c), course_titles.fetchall())


def find_evals(args_from_ui):
    '''
    Information from evaluations only.

    Input:
        args_from_ui: A dicionary, a list of arguments from the user.

    Output:
        a sql query
    '''
    
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()

    extra = "GROUP BY professor;"
    args_list = []
    args_list.append(args_from_ui['dept'])
    args_list.append(args_from_ui['course_num'])
    args_list.append(args_from_ui['year'])
    args_list.append(args_from_ui['quarter'])
    if 'professor' in args_from_ui:
        cleaned = " ".join(args_from_ui['professor'].split())
        cleaned = cleaned.upper()
        args_list.append(cleaned)
        extra = " AND professor = ? GROUP BY professor;"


    query = ('SELECT dept, course_num, title, professor, prof_sentiment, ' 
    'course_sentiment,' 
    'enrollment FROM courses JOIN instructor_sentiment JOIN class_sentiment ' 
    'JOIN overview ON '
    'courses.course_id = instructor_sentiment.course_id ' 
    'AND instructor_sentiment.course_id = class_sentiment.course_id AND ' 
    'class_sentiment.course_id = overview.course_id '
    'WHERE courses.dept = ? AND '
    'courses.course_num = ? AND overview.year = ? AND overview.quarter = ?')
    query += extra

    course_titles = c.execute(query, args_list)

    return (get_header(c), course_titles.fetchall())


def find_syllabi(args_from_ui):
    '''
    SQL query for when syllabi information is available only.

    Inputs:
        args_from_ui: A dictionary with arguments from the user.

    Outputs:
        a queried sql db.
    '''
    
    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()

    extra = "GROUP BY professor LIMIT 1;"
    args_list = []
    args_list.append(args_from_ui['dept'])
    args_list.append(args_from_ui['course_num'])
    args_list.append(args_from_ui['year'])
    args_list.append(args_from_ui['quarter'])
    if 'professor' in args_from_ui:
        cleaned = " ".join(args_from_ui['professor'].split())
        cleaned = cleaned.upper()
        args_list.append(cleaned)
        extra = " AND professor = ? GROUP BY professor LIMIT 1;"


    query = ('SELECT dept, course_num, title, professor, ' 
    'num_due, grade_breakdown, office_hours, by_appointment '
    'FROM courses ' 
    'JOIN overview JOIN days_off ON '
    'courses.course_id = days_off.course_id AND ' 
    'overview.professor_id = days_off.professor_id '
    'WHERE dept = ? AND '
    'course_num = ? AND days_off.year = ? AND days_off.quarter = ?')
    query += extra

    course_titles = c.execute(query, args_list)

    return (get_header(c), course_titles.fetchall())


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


def searcher(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for find_courses
            args = {}
            instructors = form.cleaned_data['professor']
            if instructors:
                args['professor'] = instructors
            dept = form.cleaned_data['dept']
            if dept:
                args['dept'] = dept
            course_num = form.cleaned_data['course_num']
            if course_num:
                args['course_num'] = course_num
            quarter = form.cleaned_data['quarter']
            if quarter:
                args['quarter'] = quarter
            year = form.cleaned_data['year']
            if year:
                args['year'] = year

            res = find_syllabi_and_evals(args)
            if res[1] == []:
                res = find_evals(args)
                if res[1] == []:
                    res = find_syllabi(args)
                    if res[1] == []:
                        res = None

    else:
        form = SearchForm()

    # Handle different responses of res

    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = "Sorry! We don't yet have this information."
        context['err'] = res
        result = 'string result'
    else:
        columns, result = res

            # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)

        d = {
        'dept': 'Department',
        'course_num': 'Course Number',
        'title': 'Title',
        'professor': 'Professor',
        'prof_sentiment': 'Professor Sentiment',
        'course_sentiment': 'Course Sentiment',
        'num_due': 'Holiday Assignments',
        'grade_breakdown': 'Grade Breakdown',
        'by_appointment': 'By Appointment',
        'enrollment': 'Enrollment',
        'office_hours': 'Office Hours',
        'hrs_per_student': 'Office Hours per Student'
        }
        new_col = []
        for col in columns:
            if col in d:
                col = d[col]
                new_col.append(col)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in new_col]

    context['form'] = form
    return render(request, 'searcher/index.html', context)

