'''
Academic calendar reading functions
'''
import datetime
import re
import requests
import bs4

calendar_dict = {"January": 1, "February": 2, "March": 3, "April": 4, \
"May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, \
"November": 11, "December": 12}

dates_desired = {"Autumn": ["Thanksgiving", "Reading Period"], "Winter": \
["Martin Luther King", "MLK", "M.L.K", "College Break", "Reading Period"],\
"Spring" : ["Memorial", "Reading Period"]}


def calendar_scraper(quarter, year):
    '''
    Gives a calendar with the dates of holidays.

    Inputs:
        quarter: Autumn, Winter, Spring (str)
        year: calendar year desired (4 digit integer)

    Returns:
        dates: a list of HTML tags and text containing the day off and name of
            holiday
    '''

    if quarter == 'Autumn':
        yearspan = (year, year + 1)
    else:
        yearspan = (year - 1, year)

    data = {'year': str(yearspan[0]) + '%E2*80%93' + str(yearspan[1])}
    url = 'https://events.uchicago.edu/academic/calendar/past.php'
    response = requests.post(url, data = data)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')  
    good_table = soup.find(name='h3', text = quarter + ' ' + \
        str(year)).find_next_sibling(name='table')
    dates = good_table.find_all('tr')
    return dates


def collect_important_days(quarter, year):
    '''
    Parses UChicago's online archived academic calendars and collects relevant
    dates.

    Input:
        quarter: a string (ex:"Autumn 2017") for determining the dates off.
        year: calendar year desired (4 digit integer)

    Outputs:
        relevant_dates: a list of tuples having all of the "important dates" 
          for a given quarter and year in the academic calendar. The first 
          element in the tuple is a date or a range of dates that corresponds 
          to a relecant date. The second element of the tuple is the name of 
          the relevant date.
    '''

    days_off = []
    quarter = quarter[0].upper() + quarter[1:].lower()
    if quarter == "Fall":
        quarter = "Autumn"

    tr_table = calendar_scraper(quarter, year)[1:]
    raw_date_strings = [' '.join(i.text.split()) for i in tr_table]
    
    relevant_dates = []
    for i in raw_date_strings:
        match = re.match(r'\w+.\w+?,\s(\w+\s\d+.?\d{0,3}?)\s(.*)', i).groups()
        relevant_dates.append(match)
    
    return relevant_dates


def split_dates(relevant_dates):
    '''
    Splits up days in the calendar so there is only one day corresponding to
    each holiday even when the holiday is 2 days long (e.g. converts 
    [("November 24-25", "Thanksigiving")] to [("November 24", "Thanksgiving"),
    ("November 25", "Thanksgiving")]). Also handles the case where month/day
    pairs are from different months

    Input:
        relevant_dates: a list of tuples containing relevant dates in a given
            quarter/year pair.

    Output:
        splitted_dates: a list of tuples containing relative dates splitted
            as described above.
    '''

    splitted_dates = []
    days_off = []
    for i in relevant_dates:
        if (("–" in i[0]) or ("-" in i[0])):
            month, days = i[0].split()
            split_date = days.split("–")
            if type(split_date) == str:
                split_date = days.split("-")

            # split month cases, e.g. "November 30-1 "   
            if int(split_date[0]) > int(split_date[1]):
                month_val = calendar_dict[month] + 1
                if month_val == 13:
                    month_val = 1
                next_month = list(calendar_dict.keys())\
                [list(calendar_dict.values()).index(month_val)]
                splitted_dates.append((month + " " + split_date[0], i[1]))
                splitted_dates.append((next_month + " " + split_date[1], i[1]))
            else:
                dates = [month + " " + day for day in split_date]
                for date in dates:
                    splitted_dates.append((date, i[1]))
        else:
            splitted_dates.append(i)

    return splitted_dates


def find_holiday(splitted_dates, quarter):
    '''
    Finds relevant holidays for a given quarter.

    Inputs:
        splitted_dates: a list of tuples with cleaned and splitted date tuples
        as described in the split_dates function
        quarter: the quarter the splitted_dates correspond to.
    Output:
        holidays: a list of tuples. The first element of the tuple is a single
            date in the format "Month, DD" and the second element of the tuple
            is the name of the corresponding university holiday.
    '''

    days_off = []
    for i in splitted_dates:
        if any(x in i[1] for x in dates_desired[quarter]):
            days_off.append(i)

    return days_off

def convert_to_datetime(holidays, year):
    '''
    Coverts list of dates associated with holidays to datetime objects

    Inputs:
        holidays: a list of tuples. The first element of the tuple is a single
            date in the format "Month, DD" and the second element of the tuple
            is the name of the corresponding university holiday.
        year: calendar year desired (4 digit integer)

    Output:
        Dictionary mapping names of holidays their associated datetime object 
          for each year
    '''
    datetimes_dict = {}
    for date, holiday in holidays:
        month, day = date.split(" ")
        month_num = calendar_dict[month]
        day = int(day)
        if holiday in datetimes_dict:
            datetimes_dict[holiday].append(datetime.date(year, month_num, day))
        else:
            datetimes_dict[holiday] = [datetime.date(year, month_num, day)]

    return datetimes_dict


def get_datetimes_from_calendar(quarter, year):
    '''
    Gets datetime objects for holidays in a given quarter and year 

    Inputs:
        quarter: a string indicating the quarter, either 'Autumn', 'Winter', 
          or 'Spring'
        year: calendar year desired (4 digit integer)

    Output: dictionary mapping holiday names to datetime objeccts assocaited 
    '''

    relevant_dates = collect_important_days(quarter, year)
    splitted_dates = split_dates(relevant_dates)
    days_off = find_holiday(splitted_dates, quarter)
    datetimes_dict = convert_to_datetime(days_off, year)

    return datetimes_dict
