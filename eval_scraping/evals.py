from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
import csv
import bs4
import re


def gogo_gadget_browser(username, password):
    '''
    Helper function for initializing the web browser. Returns a browser object 
    with cookies saved so websites can be iterated through without getting 
    locked out of them.

    Inputs:
        username: a valid CNET username
        password: a valid CNET password

    Outputs:
        browser: A webdriver object from which we can collect evals.
    '''

    fp = webdriver.FirefoxProfile('/home/student/.mozilla/firefox')
    browser = webdriver.Firefox(fp)

    browser.get(('https://registrar.uchicago.edu/registration/college-process/'
        'course-evaluations/'))
    request_cookies_browser = browser.get_cookies()
    browser.find_element_by_css_selector('.et_pb_button').click()
    time.sleep(3)
    username = browser.find_element_by_id('username').send_keys(username)
    password = browser.find_element_by_id('password').send_keys(password)
    browser.find_element_by_name('_eventId_proceed').click()
    time.sleep(3)
    browser.find_element_by_css_selector(('div.form-item:nth-child(2) >'
        'p:nth-child(2) > label:nth-child(1)')).click()

    return browser


def csv_writer(eval_dict, attribute_keys, filename, Course_Num, relevant_prof):
    '''
    Helper function for appending to a csv file.

    Inputs:
        eval_dict: A dictionary. Maps eval subheaders to a list of student
            responses to questions in that key subheader.
        attribute_keys: Keys of interest for a given eval to access and 
        write to the csv file.
        filename: The desired filename for the csv file.
        Course_Num: The course number of the given class being appended 
            to the csv file.
        relevant_prof: A string, the professor that taught the relevant class.

    Outputs: 
        None. writes to a csv file. Each row of the csv file contains a 
            single student response to an eval question.
    '''

    with open(filename, mode = "a") as csvfile:
        csvfile1 = csv.writer(csvfile)
        for attribute in attribute_keys:
            if attribute in eval_dict.keys():
                for row in eval_dict[attribute]:
                    csvfile1.writerow([Course_Num, relevant_prof, row])


def scrape_eval(course_list, cnet, password):
    '''
    Given a course list, collects all the evals associated with all of the 
    classes in the course list.

    Inputs:
        course_list: A pandas DataFrame with the following elements: A unique
            course ID (Course_Num), a department for a class (Dept), and a 
            number for the class (Number).

    Outputs:
        None, but writes 3 CSV files:
            instructor_emotions.csv: each row contains a unique course ID,
                a professor name, and a single student response to a question
                about the professor.
            class_emotions.csv: each row contains a unique course ID, a
                professor name, and a single student response to a question 
                about the class.
            courses.csv: each row contains a unique course ID, a quarter the
                class was offered, and a year the class was offered.
    '''

    browser = gogo_gadget_browser(cnet, password)

    for i in course_list.itertuples():
        current_url = ('https://evaluations.uchicago.edu/index.php?' + 
        'EvalSearchType=option-number-search&Department=&AcademicYear=&'+ 
        'CourseDepartment=' + i.Dept + '&CourseNumber=' + str(i.Num) + 
        '&InstructorLastName=&advancedSearch=SEARCH')
        browser.get(current_url)
        html_source = browser.page_source
        soup = bs4.BeautifulSoup(html_source, 'lxml')

        if len(soup.find_all("div", {"class": "messages error"})) == 0:

            evals_to_soup = soup.find_all("td")[0::4]
            prof_names = soup.find_all("td")[2::4]
            quarter_offered = soup.find_all("td")[3::4]

            for idx, e in enumerate(evals_to_soup):
                d = {}
                relevant_prof = prof_names[idx].text
                quarter, year = quarter_offered[idx].text.split(" ")
                d[e.a['href']] = {}
                browser.get('https://evaluations.uchicago.edu/' + e.a['href'])
                eval_html_source = browser.page_source
                eval_soup = bs4.BeautifulSoup(eval_html_source, 'lxml')
                enrollment = get_enrollment(eval_soup)
                for header in eval_soup.find_all('h2'):
                    d[e.a['href']][header.text] = []
                    nextNode = header
                    while True:
                        nextNode = nextNode.findNext('ul')
                        if nextNode is None:
                            break
                        elif nextNode.name == 'ul':
                            if nextNode.find_all('li'):
                                for li in nextNode.find_all('li'):
                                    d[e.a['href']][header.text].append(li.text)

                csv_writer(d[e.a["href"]], ["General Information:", \
                    "Course Work", "The Course", "Assignments and Tests",\
                    "Laboratories (if applicable"], "class_emotions.csv", \
                    i.Course_Num, relevant_prof)

                csv_writer(d[e.a["href"]], ["The Instructor", \
                    "Evaluation Comments", "Comments"], \
                    "instructor_emotions.csv", i.Course_Num, relevant_prof)

                with open("courses.csv", mode = "a") as courses_file:
                    courses1 = csv.writer(courses_file)
                    courses1.writerow([i.Course_Num, quarter, year])

                with open("enrollment.csv", mode = "a") as enrollment_file:
                    enroll = csv.writer(enrollment_file)
                    enroll.writerow([i.Course_Num, quarter, year, \
                    	relevant_prof, enrollment])
  
                
def get_enrollment(eval_soup):  
    '''
    Gets the enrollment for a course

    Inputs:
        eval_soup: a beautiful soup object

    Returns:
        None: if the information is not supplied
        enrollment: integer that gives the enrollment for that course
    '''
    enrollment = eval_soup.find('strong', text='Number Enrolled:')
    if enrollment is not None:
        enrollment = enrollment.next_sibling
        enrollment = re.search(r'\d+', enrollment)
        enrollment = enrollment.group(0)
        return enrollment
    return None
