import os
import re
import textract
import util
import calendar_scraper as cs


def count_off_day_assignments(text, year):
    '''
    Counts the number of assignments due on an off-day in a course syllabus 
    from a given year in spring quarter

    Inputs:
        text: (str) The contents of a syllabus PDF.
        year: calendar year desired (4 ints)

    Returns:
        The number of assignments due on an off day during the course (int)
        If the syllabus does not mention the off day, either by name or date, 
        we return 'Note Enough Information Available'
    '''
    key_words = [
    'due', 'assignment', 'paper', 'deadline', 'project', 'presentation', \
    'turn in', 'submission', 'final']
    month_formats = [
            'march','april','may','june','mar','apr','jun','mar.','apr.',\
            'jun.', 'week']

    # Get Memorial Day Formats
    MEMORIAL_DAY_FORMATS = ['memorial day']
    memorial_numerical = util.get_numerical_formats(\
        "Spring", year, "Memorial Day")
    MEMORIAL_DAY_FORMATS.extend(memorial_numerical)            

    # Get Reading Period Formats 
    READING_PERIOD = ["reading period", "reading days"]
    reading_period_numerical = util.get_numerical_formats(\
        "Spring", year, "College Reading Period")
    READING_PERIOD.extend(reading_period_numerical)


    num_memorial, memorial_check_list = util.get_num_assignments(
        MEMORIAL_DAY_FORMATS, text, month_formats, key_words)
    num_rp, rp_check_list = util.get_num_assignments(READING_PERIOD, text, \
    	month_formats, key_words)

    check_list = memorial_check_list + rp_check_list
    num_due_assignments = num_memorial + num_rp

    for i in check_list:
        if i is not None: 
            return num_due_assignments
            
    return 'Not enough information available.'


