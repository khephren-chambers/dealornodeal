import os
import re
import textract
import util
import calendar_scraper as cs


def count_off_day_assignments(text, year):
    '''
    Counts the number of assignments due on an off-day in a course syllabus 
    from a given year in autumn quarter

    Inputs:
        text: (str) The contents of a syllabus PDF
        year: calendar year desired (4 ints)

    Output:
        The number of assignments due on an off day during the course (int)
        If the syllabus does not mention the off day, either by name or date, 
        we return 'Note Enough Information Available'
    '''
    key_words = [
    'due', 'assignment', 'paper', 'deadline', 'project', 'presentation', \
    'turn in', 'submission', 'final']
    month_formats = [
            'sep','oct','nov','dec','september','october','november',\
            'december','sep.','oct.','nov.','dec.','week']
    
    # Get Thanksgiving Break Formats
    THANKSGIVING_FORMATS = ['thanksgiving']
    thanksgiving_numerical = util.get_numerical_formats(\
        "Autumn", year, "Thanksgiving Break")
    THANKSGIVING_FORMATS.extend(thanksgiving_numerical)

    # Get Reading Period Formats
    READING_PERIOD = ["reading period", "reading days"]
    reading_period_numerical = util.get_numerical_formats(\
        "Autumn", year, "College Reading Period")
    READING_PERIOD.extend(reading_period_numerical)

    
    num_thanksgiving, thanksgiving_check_list = util.get_num_assignments(
        THANKSGIVING_FORMATS, text, month_formats, key_words)
    num_rp, rp_check_list = util.get_num_assignments(READING_PERIOD, text, \
    	month_formats, key_words)

    check_list = thanksgiving_check_list + rp_check_list
    num_due_assignments = num_thanksgiving + num_rp

    for i in check_list:
        if i is not None: 
            return num_due_assignments
            
    return 'Not enough information available.' 


