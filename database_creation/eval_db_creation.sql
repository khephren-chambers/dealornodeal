CREATE TABLE courses
(course_id integer,    -- unique course ID
dept VARCHAR(4), -- 4 letter department code
course_num integer, -- 5 digit course number
title TEXT -- course title
);

CREATE TABLE instructor_sentiment
(course_id integer, -- unique course ID
professor_id integer, -- unique ID assigned to each professor
prof_sentiment TEXT -- sentiment score for professor
);

CREATE TABLE class_sentiment
(course_id integer, -- unique course ID
professor_id integer,  -- unique ID assigned to each professor
course_sentiment TEXT -- sentiment score for professor
);

CREATE TABLE overview
(course_id integer, -- unique course ID
quarter VARCHAR(6), -- quarter class is offered
year integer, -- year class is offered
professor TEXT, -- professor name
enrollment integer, -- number enrolled in course
professor_id integer -- unique ID assigned to each professor
);

CREATE TABLE days_off
(course_id integer, -- unique course ID
quarter VARCHAR(6), -- quarter class is offered
year integer, -- year class is offered
num_due VARCHAR(7), -- number assignments due on days off
grade_breakdown TEXT, -- grade breakdown for the class
office_hours integer, -- number of office hours
by_appointment VARCHAR(4), -- office hours by appt?
professor_id integer -- unique ID assigned to each professor
);

.import courses_final.csv overview
.import professor_final.csv instructor_sentiment
.import cemo_final.csv class_sentiment
.import course_list_final.csv courses
.import due_dates_final_1.csv days_off