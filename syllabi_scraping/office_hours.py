import os
import re
import util
import textract
import datetime as dt


NORMAL_REGEX = [r"([a-z./,]+) (\d{1,2}\:?\d*\s?[amp\.]*)\s?[-–]\s?(\d{1,2}\:?"
r"\d*\s?[amp\.]*)",
r"([a-z./,]+) (\d{1,2}\:?\d*\s?[amp\.]*)\sto\s(\d{1,2}\:?\d*\s?[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\s?[-–]\s?(\d{1,2}\:?\d*"
r"\s?[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\sto\s(\d{1,2}\:?\d*\s?"
r"[amp\.]*)"]

NOON_REGEX = [
r"([a-z./,]+) (noon)\s?[-–]\s?(\d{1,2}\:?\d*\s?[amp\.]*)",
r"([a-z./,]+) (noon)\sto\s(\d{1,2}\:?\d*\s?[amp\.]*)",
r"([a-z./,]+) (\d{1,2}\:?\d*\s?[amp\.]*)\s?[-–]\s?(noon)",
r"([a-z./,]+) (\d{1,2}\:?\d*\s?[amp\.]*)\sto\s(noon)"]

DOUBLE_REGEX = [
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\s?[-–]\s?(\d{1,2}\:?\d*"
r"\s?[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\sto\s(\d{1,2}\:?\d*\s?"
r"[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (noon)\s?[-–]\s?(\d{1,2}\:?\d*\s?[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (noon)\sto\s(\d{1,2}\:?\d*\s?[amp\.]*)",
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\s?[-–]\s?(noon)",
r"([a-z.]+ [and&]+ [a-z.]+) (\d{1,2}\:?\d*\s?[amp\.]*)\sto\s(noon)",
]

ALL_REGEX = DOUBLE_REGEX + NOON_REGEX + NORMAL_REGEX

CLEAN_DICT = {
    '1': "13:00",
    '2': "14:00",
    '3': "15:00",
    '4': "16:00",
    '5': "17:00",
    '6': "18:00",
    '7': "7:00",
    '8': "8:00",
    '9': "9:00",
    '10': "10:00",
    '11': "11:00",
    '12': "12:00",
    '13': "13:00",
    '14': "14:00",
    '15': "15:00",
    '16': "16:00",
    '17': "17:00",
    '18': "18:00"
}


def calc_office_hours(text, year):
    '''
    Calculates the total number of office hours in a course syllabus. 
    Also reports if there are additional office hours "by appointment".

    Inputs:
        text: (str) The text of the syllabus.
        year: (int) The year of the course the syllabus corresponds to.

    Returns:
        The total number of office hours, and a boolean representing if there
          are "by appointment" office hours.
    '''

    check_string = ""
    r = re.search('office hours', text)
    if r is None:
        return 'N/A', 'N/A'
    indices = r.span()
    oh_text = text[indices[1] + 1:indices[1] + 400]
    oh_text = clean_office_hours_text(oh_text)
    office_hours = []
    for regex in ALL_REGEX:
        office_hours.extend(re.findall(regex, oh_text))
    total_hours = 0.0
    for result in office_hours:
        check_result = turn_into_string(result)
        if check_result not in check_string:
            time_1 = clean_time(result[1])
            time_2 = clean_time(result[2])
            if (time_1 is None) or (time_2 is None):
                continue
            if is_two_days(result):
                total_hours += calculate_hours(time_1, time_2) * 2
                check_string += check_result
            else:
                total_hours += calculate_hours(time_1, time_2)
    
    appointment = is_by_appointment(oh_text)

    return total_hours, appointment


def clean_office_hours_text(text):
    '''
    Cuts off text in a syllabus PDF following the string 'office hours' so that
    irrelevant text that was initially scraped is discarded.

    Inputs:
        text: (str) 400 characters following the string 'office hours' in the
          full text of a syllabus PDF.
    '''

    stopping_conditions = ['sec.', 'section', 'lec.', 'lecture', '[', \
    'problem', 'discussion', 'description', 'phone']
    for stop in stopping_conditions:
        index = text.find(stop)
        if index != -1:
            text = text[:index]

    return text


def clean_time(time):
    '''
    Cleans a time string so that it follows a uniform style.

    Inputs:
        time: (str) A string representing a time.

    Outputs:
        The time string, cleaned.
    '''

    if time == 'noon':
        return "12:00"

    new_time = ""
    hour, minutes = re.findall(r"(\d{1,2})\:?(\d?\d?)", time)[0]
    try:
        hour = CLEAN_DICT[hour]
    except:
        hour = None
    if hour is None:
        return None
    new_time += hour

    if len(minutes) != 0:
        new_time = new_time[:-2] + minutes

    return new_time


def calculate_hours(time_1, time_2):
    '''
    Calculates the number of hours between a starting and ending time.

    Inputs:
        time_1: (str) A string representing a starting time.
        time_2: (str) A string representing an ending time.

    Returns:
        The number of hours between the starting and ending time.
    '''

    time_1 = dt.datetime.strptime(time_1, '%H:%M')
    time_2 = dt.datetime.strptime(time_2, '%H:%M')
    difference = time_2 - time_1
    difference = difference.total_seconds()
    difference = difference / 3600

    return difference


def is_two_days(result):
    '''
    Determines if a single timeframe for office hours (e.g.: '10-12pm') is for
    two days or just one.

    Inputs:
        result: (tuple) The result of a regex find in text pertaining to office
          hours. 

    Returns:
        Whether or not the timeframe is for two days.
    '''

    days = result[0]
    check_slash = re.search(r"\w+\/\w+", days)
    if check_slash is not None:
        return True
    if ('and' in days) or ('&' in days):
        if days == 'and':
            return False
        checks = ['mon', 'tu', 'wed', 'th', 'fri', 'sat', 'sun']
        counts = 0
        for day in checks:
            if day in days:
                counts += 1
        if counts < 2:
            return False
        else:
            return True


def is_by_appointment(text):
    '''
    Determines whether or not office hours are offered "by appointment".

    Inputs:
        text: a string of text pertaining to office hours.

    Returns:
        A string representing whether or not office hours are offered "by 
        appointment".
    '''

    terms = ['appointment', 'appt', 'apt', 'apptmt', 'by request', \
    'schedule a meeting', 'additional', 'schedule a meeting']

    for term in terms:
        if term in text:
            return 'Yes'

    return 'No'


def turn_into_string(result):
    '''
    Turns a tuple obtained from a regular expression find into a string.

    Inputs:
        result: (tuple) A tuple containing a "day", start time, and end time.

    Returns:
        The tuple converted into a string.
    '''

    s = ""
    for i in result:
        s += i + " "

    return s