import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ANALYZER = SentimentIntensityAnalyzer()
CSV_FILES = ["instructor_emotions.csv", "enrollment.csv", \
"class_emotions.csv", "cleaned_course_list.csv", "demo.csv"]


def hash_val(prof_name):
    '''
    Hash value function for getting professor IDs from professor names.

    Inputs:
        prof_name: A string, a professor's name.

    Oututs:
        hash_value: An integer
    '''
    if type(prof_name) == str:
        prof_name = "".join(prof_name.split())
        hash_value = 0

        for character in prof_name:
            hash_value *= 2
            hash_value += ord(character)
            hash_value %= 2000000000

        return hash_value
        
    pass


def normalizer(name):
    '''
    Eval normalizer to strip extraneous whitespace from evals.

    Inputs:
        name: a string, an evaluation.

    Outputs:
        name: a string, a cleaned evaluation.
    '''
    name = " ".join(name.split())

    return name


def clean(inst_emo, enroll, class_emo, course_list, due_dates):
    '''
    Cleans raw scraped csv files.

    Inputs:
        inst_emo: file name for instructor evals
        enroll: file name for csv with enrollment info
        class_emo: file name for class evals.
        course_list: file name for csv with course list info.
        due_dates: file name for csv with due dates/office hours info.

    Outputs:
        None, just writes changes to csv files
    '''

    prof = pd.read_csv(inst_emo, names = ["Course_ID", "Professor", "Eval"])
    times = pd.read_csv(enroll, names = ["Course_ID", "Quarter", "Year",\
    "Professor", "Enrollment"])
    c_emo = pd.read_csv(class_emo, names = ["Course_ID", "Professor", "Eval"])
    course_list = pd.read_csv(course_list).drop_duplicates(["Dept", "Num"]).\
        rename(columns = {"Course_Num": "Course_ID"})
    due_dates = pd.read_csv(due_dates, header = 0, sep = "|").\
        rename(columns = {"Course_Num": "Course_ID"})

    c_emo.dropna(inplace = True)
    prof.dropna(inplace = True)
    times.dropna(inplace = True)

    prof["Prof_ID"] = prof["Professor"].str.upper()
    prof["Prof_ID"] = prof["Prof_ID"].apply(hash_val)

    prof = prof[prof["Prof_ID"] >= 0]
    prof = prof[prof["Course_ID"].isin(times["Course_ID"])]

    c_emo["Prof_ID"] = c_emo["Professor"].str.upper()
    c_emo["Prof_ID"] = c_emo["Prof_ID"].apply(hash_val)
    c_emo = c_emo[c_emo["Course_ID"].isin(times["Course_ID"])]

    times["Prof_ID"] = times["Professor"].str.upper()
    times["Prof_ID"] = times["Prof_ID"].apply(hash_val)
    times.Prof_ID = times.Prof_ID.astype(int)
    times.Professor = times.Professor.str.upper()

    due_dates["Prof_ID"] = due_dates["Professor"].str.upper()
    due_dates["Prof_ID"] = due_dates["Prof_ID"].apply(hash_val)
    due_dates.Prof_ID.fillna(0, inplace = True)
    due_dates.Prof_ID = due_dates.Prof_ID.astype(int)
    due_dates.Professor = due_dates.Professor.str.upper()   

    prof.drop(["Professor"], axis = 1, inplace = True)
    prof["Eval"] = prof["Eval"].apply(normalizer)
    c_emo.drop(["Professor"], axis = 1, inplace = True)
    c_emo["Eval"] = c_emo["Eval"].apply(normalizer)
    due_dates.drop(["Professor"], axis = 1, inplace = True)

    c_emo.dropna(inplace = True)
    prof.dropna(inplace = True)
    due_dates.dropna(inplace = True)

    c_emo["Eval"] = c_emo["Eval"].apply(sentiment_numbers)
    c_emo.Prof_ID = c_emo.Prof_ID.astype(int)
    c_emo = c_emo.groupby(["Course_ID", "Prof_ID"]).mean().reset_index()
    c_emo["Eval"] = c_emo["Eval"].apply(sentiment_analyzer_scores)

    prof["Eval"] = prof["Eval"].apply(sentiment_numbers)
    prof = prof.groupby(["Course_ID", "Prof_ID"]).mean().reset_index()
    prof["Eval"] = prof["Eval"].apply(sentiment_analyzer_scores)
    prof.Prof_ID = prof.Prof_ID.astype(int)
    
    course_list.Title = course_list.Title.astype(str)
    course_list.Dept = course_list.Dept.astype(str)
    course_list.Num = course_list.Num.astype(int)
    course_list.Course_ID = course_list.Course_ID.astype(int)

    prof.drop_duplicates(inplace = True)
    times.drop_duplicates(inplace = True)
    c_emo.drop_duplicates(inplace = True)
    course_list.drop_duplicates(inplace = True)
    due_dates.drop_duplicates(inplace = True)

    export(prof, times, c_emo, course_list, due_dates)


def sentiment_numbers(sentence):
    '''
    Calculates sentiment scores for a given sentiment string.

    Inputs: 
        sentence: A string, an eval for the sentiment analysis.

    Outputs:
        a sentiment score as an integer from -1 to 1.
    '''

    if type(sentence) == str:
        return ANALYZER.polarity_scores(sentence)["compound"]
    pass


def sentiment_analyzer_scores(score):
    '''
    Calculates a category for a given sentiment score.

    Inputs:
        score: A float, a sentiment score from the sentiment analysis.

    Outputs:
        a string, representing the category of the sentiment analysis.
    '''

    if type(score) == float:        
        if score <= -.19673:
            return 'Extremely Negative'
        elif score <= -.005:
            return 'Slightly Negative'
        elif score <= .005:
            return 'Neutral'
        elif score <= .41950:
            return 'Slightly Positive'
        elif score > .41950:
            return 'Extremely Positive'
    pass


def export(prof, times, c_emo, course_list, due_dates):
    '''
    Exports pd dfs to workable csv files for sql database.

    Inputs:
        pandas dfs with info corresponding to their csv inputs in clean().

    Outputs:
        None. just writes dfs to csv files.
    '''

    times.to_csv("courses_final.csv", index = False, sep ="|")
    prof.to_csv("professor_final.csv", index = False, sep = "|")
    c_emo.to_csv("cemo_final.csv", index = False, sep = "|")
    course_list.to_csv("course_list_final.csv", index = False, sep = "|")
    due_dates.to_csv("due_dates_final.csv", index = False, sep = "|")

