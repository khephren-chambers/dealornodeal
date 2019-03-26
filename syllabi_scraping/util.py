import os
import re
import calendar_scraper as cs
import textract
import instructor 


DATE_FORMATS = {
    '1': "Jan {}, January {},  1/{}, Jan {}{}, January {}{}, Jan. {}",
    '2': "Feb {}, February {},  2/{}, Feb {}{}, February {}{}, Feb. {}",
    '3': "Mar {}, March {},  3/{}, Mar {}{}, March {}{}, Mar. {}",
    '4': "Apr {}, April {},  4/{}, Apr {}{}, April {}{}, Apr. {}",
    '5': "May {}, May {},  5/{}, May {}{}, May {}{}",
    '6': "Jun {}, June {}, 6/{}, Jun {}{}, Jun {}{}, Jun. {}",
    '11': "Nov {}, November {}, 11/{}, Sep {}{}, Sep {}{}, Sep. {}",
    '12': "Dec {}, December {}, 12/{}, Dec {}{}, Dec {}{}, Dec. {}"
}

DAY_SUFFIXES = {
    '1': "st",
    '2': "nd",
    '3': "rd",
    '4': "th",
    '5': "th",
    '6': "th",
    '7': "th",
    '8': "th",
    '9': "th",
    '0': "th"
}


def clean_pdf(directory, syllabus):
    '''
    Cleans a textracted PDF file containing a syllabus: decodes it from utf-8
    format into string text, replaces all special whitespace characters with
    a single white space, and converts the string to all lowercase. Essentially
    makes a textracted PDF easier to read.

    Inputs:
        syllabus: (str) Path to a single PDF file containing a syllabus.

    Returns:
        The cleaned, easier-to-read PDF text.
    '''

    syllabus_text = textract.process(directory + "/" + syllabus)
    syllabus_text = syllabus_text.decode('utf-8')
    syllabus_text = re.sub(r"\s+", ' ', syllabus_text)
    syllabus_text = re.sub(r"\xad", "-", syllabus_text)
    syllabus_text = re.sub(r"\–", "-", syllabus_text)
    syllabus_text = syllabus_text.lower()

    return syllabus_text


def iterate_professors(directory):
    '''
    Iterates over all syllabi in a directory and returns a 
    dictionary mapping a course name to a professor name 

    Inputs: 
        directory: (str) Path to the directory containing syllabi as PDFs.
    
    Return: 
        A dictionary mapping each course to the professor name
    '''

    syllabi_dict = {}

    for folder in os.listdir(directory):
        quarter = re.search(r'\D+', folder).group()
        quarter = quarter[0].upper() + quarter[1:]
        year = '20' + re.search(r'\d+', folder).group()
        subdirectory = directory + "/" + folder
        for syllabus in os.listdir(subdirectory):
            syllabus_text = clean_pdf(subdirectory, syllabus)
            dept = re.search(r'[A-Z]{4}', syllabus).group()
            course_num = re.search(r'\d{5}', syllabus).group()
            syllabi_dict[subdirectory+syllabus] = instructor.get_professor(
                syllabus_text, quarter, year, dept, course_num)   

    return syllabi_dict


def iterate_through_syllabi(directory, function, year):
    '''
    Carries out a regular expression function on all syllabi in a directory,
    and returns a dictionary mapping each course to the regex function output.

    Inputs:
        directory: (str) Path to the directory containing syllabi as PDFs.
        function: A function containing regular expressions that will be 
          applied to the text of the syllabi.
        year: (int) year (eg 2018, 2019 etc.)
    
    Returns:
        A dictionary mapping each course to the function output.
    '''

    syllabi_dict = {}
    for syllabus in os.listdir(directory):
        syllabus_text = clean_pdf(directory, syllabus)
        syllabi_dict[syllabus] = function(syllabus_text, year)    

    return syllabi_dict


def check_string(check_this_before, check_this_after, month_formats):
    '''
    splits string surrounding off day string into list of words and 
    checks it for other dates or key words that might mislead the function 
    that searches of assignments on off days and splices string for only relevant 
    surrounding words

    Inputs: 
        check_this_before: string before off day string to check
        check_this_after: string after off day string to check
        month_formats: months to look for based on which quarter 

    Returns: 
        list of words to search for key words 
    '''

    month_formats += re.findall(r'\d{1,2}/\d{1,2}', check_this_before)
    month_formats += re.findall(r'\d{1,2}/\d{1,2}', check_this_after)
    month_formats += ['m','w','th','f']
    check_this_before = check_this_before.split()
    check_this_after = check_this_after.split()
    new_list_before = check_this_before

    for word in check_this_before:
        if word in month_formats:
            num = check_this_before.index(word)
            new_list_before = new_list_before[num + 1:]
    new_list_after = check_this_after

    for word in check_this_after:
        if word in month_formats:
            num = check_this_after.index(word)
            new_list_after = new_list_after[:num]
    new_list = new_list_before + new_list_after

    return new_list


def get_checks(items, text):
    '''
    Gets the string of text to check around a certain indicator word 

    Inputs:
        items: the indicator word around which we need to check (a match object)
        text: the raw text being searched (str)

    Output: 
        A tuple, the first element in the tuple is the 50 characters before 
            the indicator, to check and the second element is the 50 charactrs 
            after the indicator to check 
    '''

    indicies = items.span()
    check_this_before = text[indicies[0] - 50: indicies[0]]
    check_this_after = text[indicies[1]:indicies[1] + 51]

    return check_this_before,check_this_after


def get_numerical_formats(quarter, year, off_day):
    '''
    Obtains the numerical formats for off-days in a given quarter and year, to 
    use in regular expressions to find off-days in a syllabus PDF.

    Inputs:
        quarter: (str) The quarter of interest.
        year: (int) The year of interest.
        off_day: (str) The name of the off-day we would like to obtain formats
          for.

    Returns:
        A list of strings that are the numerical formats of the off-day.
    '''

    datetime = cs.get_datetimes_from_calendar(quarter, year)
    month = str(datetime[off_day][0].month)
    day = str(datetime[off_day][0].day)
    suffix = DAY_SUFFIXES[day[-1]]

    s = DATE_FORMATS[month].format(\
        day, day, day, day, suffix, day, suffix, day)
    date_formats = s.split(", ")

    return date_formats


def get_num_assignments(formats, text, month_formats, key_words):
    '''
    Scrape text and return number of assignments due for a given holiday

    Inputs: 
        formats: formats of holiday words to check for (i.e. "MLK", "Martin Luther King Day", "MLK Day")(
            list of strings )
        text: the syllabi to scrape (str)
        month_formats: months and their formats to check the syllabi for (list of strings)
        key_words: words to check for that indicate an assignment due

    Output: 
        a tuple, where the first element of the tuple is the number of assignments due 
            and the second element of the tuple is a list of match objects to check if 
            any assignments are due in the syllabus
    '''
    
    check_list = []
    num_due_assignments = 0 
    for s in formats: 
        frag = re.search(s,text)
        check_list.append(frag)
        if frag is not None: 
            check = get_checks(frag, text)
            new_list = check_string(check[0], check[1], month_formats)
            for word in new_list: 
                if word in key_words:
                    num_due_assignments += 1 
                    break

    return (num_due_assignments, check_list) 