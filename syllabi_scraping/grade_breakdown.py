import os
import re
import textract
import util


KEY_WORDS = [r'([A-Za-z]*\s?homework[s]?)', '(quiz[zes]*)', 
r'[A-Za-z]*\s?(test[s]?)', \
'(attendance)', '(participation)', '(project[s]?)', "(response[s]?)", \
 '(presentation[s]?)', '(paper[s]?)', "(performance[s]?)", r"(mid\-?term)", \
 r"(mid\-?term [123])\s", r"(midterm\s?[sexampry]*)", r"(final\s?[sexampry]*)",\
  r'[A-Za-z]*\s?(asssignment[s]?)', r"([A-Za-z0-9\-]+)\s([A-Za-z0-9\-]{4,25})", \
  r"([A-Za-z0-9\-]{4,25})"]

PERCENTS = [
r"\s?[\:\-\,]?\s(\(?\d+\.?\d*\%\)?)",
r"\s\(.+\)\s?[\:\-\,]?\s(\(?\d+\.?\d*\%\)?)",
r"\s?[\:\-\,\=]?\s(\(?\d+\.?\d* percent\)?)",
r"\s\(.+\)\s?[\:\-\,\=]?\s(\(?\d+\.?\d* percent\)?)",
r"\s?[\:\-\,]?\s(\(?\d+\.?\d*\% of [A-Za-z]+ [A-Za-z]+\)?)",
r" counts for (\d+\.?\d*\% of [A-Za-z]+ [A-Za-z]+)",
r" will count for (\d+\.?\d*\% of [A-Za-z]+ [A-Za-z]+)",
]


def get_grade_breakdown(text, year):
    '''
    Tries multiple regex to obtain grade breakdown from course syllabi.

    Inputs:
        text: (str) The text of a syllabus PDF.

    Returns:
        The grade breakdown in the syllabi for the course.
    '''

    grade_components = []
    done = ""

    # trying regex in text
    for word in KEY_WORDS:
        for percent in PERCENTS:
            results = re.findall(r"" + word + percent, text)
            if results:
                for result in results:
                    results = results[0]
                    check_this = result[-2] + result[-1]
                    check_this = check_this.replace(" ", "")
                    if check_this not in done:   # exclude duplicates
                        done += " " + check_this
                        grade_components.append(list(result))

    # building a string representing the breakdown
    breakdown_string = []
    done2 = ""
    for item in grade_components:
        percent = get_percent(item)
        percent += "%"
        s = ' '.join(item[:-1]) + ": " + percent
        if s not in done2:     # here excluding any duplicates
            done2 += " " + s
            breakdown_string.append(s)
    breakdown_string = "; ".join(breakdown_string)
    if not breakdown_string:
        return "No grade breakdown available."
    
    return breakdown_string


def get_percent(result):
    '''
    Gets the total percentage of a grade component, from a string.

    Inputs:
        result: (str) A regex result containing a percentage(s).

    Returns:
        The percetage(s) combined.
    '''

    percent = 0.0
    percent_list = re.findall(r"\d+\.?\d*", result[-1])
    for i in percent_list:
        percent += float(i)

    return str(percent)