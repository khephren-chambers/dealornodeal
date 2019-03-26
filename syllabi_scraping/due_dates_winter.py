import os
import re
import textract
import util
import calendar_scraper as cs



def count_off_day_assignments(text, year):
    '''
    Counts the number of assignments due on an off-day in a course syllabus 
    from a given year in winter quarter .

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
    month_formats = ['jan','feb','mar','january','february','march','jan.',\
    'feb.','mar.','week']


    MLK_FORMATS = ["mlk day", "mlk holiday", "martin luther king, jr. day", \
    "mlk", "martin luther kings’ day", "martin luther king"]
    mlk_numerical = util.get_numerical_formats(\
        "Winter", year, "Martin Luther King, Jr. Day")
    MLK_FORMATS.extend(mlk_numerical)

    
    COLLEGE_BREAK = ["college break"]
    college_break_numerical = util.get_numerical_formats(\
        "Winter", year, "College Break")
    COLLEGE_BREAK.extend(college_break_numerical)

    
    READING_PERIOD = ["reading period"]
    reading_period_numerical = util.get_numerical_formats(\
        "Winter", year, "College Reading Period")
    READING_PERIOD.extend(reading_period_numerical)


    num_mlk, mlk_check_list = util.get_num_assignments(MLK_FORMATS, text, \
    	month_formats, key_words)
    num_cb, cb_check_list = util.get_num_assignments(COLLEGE_BREAK, text, \
    	month_formats, key_words)
    num_rp, rp_check_list = util.get_num_assignments(READING_PERIOD, text, \
    	month_formats, key_words)
    check_list = mlk_check_list + cb_check_list + rp_check_list
    num_due_assignments = num_mlk + num_cb + num_rp


    for i in check_list:
        if i is not None: 
            return num_due_assignments
            
    return 'Not enough information available.'

