import re
import sqlite3


def get_professor(text, quarter, year, dept, course_num):
    '''
    Gets a list of professor(s) that are in the syllabus. If none, returns the
    most likely professors that teach the course.

    Inputs:
        text:(str) The syllabus text.
        quarter: (str) The quarter of the course.
        year: (int) The year of the course
        dept: (str) The department of the course.
        course_num: (int) The five digit course number.
    '''

    db = sqlite3.connect('evals.db')
    c = db.cursor()
    course_id = c.execute("SELECT course_id FROM courses WHERE dept = ? "
        "AND course_num = ?;", [dept, course_num]).fetchall()
    if course_id:
        course_id = course_id[0][0]
        professor_query = c.execute("SELECT professor FROM overview WHERE"
        " quarter = ? AND year = ? AND course_id = ?;", [quarter, year, \
        course_id]).fetchall()
        professors = []
        for prof in professor_query:
            professors.append(prof[0])
        if professors:
            found_profs = []
            for i in professors:
                if i.lower() in text:
                    found_profs.append(i)
            if found_profs:
                return found_profs
            else:
                return professors
        else:
            new_prof_query = c.execute("SELECT professor FROM overview WHERE"
                "course_id = ? GROUP BY professor ORDER BY COUNT(*) DESC LIMIT"
                " 3;", [course_id]).fetchall()
            new_professors = []
            for prof in new_prof_query:
                new_professors.append(prof[0])
            if new_professors:
                new_found_profs = []
                for i in new_professors:
                    if i.lower() in text:
                        new_found_profs.append(i)
                if new_found_profs:
                    return new_found_profs
                else:
                    return new_professors
            else:
                return "N/A"
    else:
        return None