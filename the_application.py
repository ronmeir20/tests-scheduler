import datetime
import random
import PySimpleGUI as sg
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#------------------------------------------
#---------Written by Ron Meir Ⓒ-----------
#------------------------------------------

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

def get_calendar_service():
    """
    This function uploads the calendar and handles security staff.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def list_events():
    """
    This function returns a list of events already occuring in the calendar
    """
    
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(
        calendarId='iw.jewish#holiday@group.v.calendar.google.com', timeMin=now,
        maxResults=50, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    the_events = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        the_events.append(start)

    return the_events


def search_in_events_list(event, event_list, tests_list):
    """
    This function returns true if the date is taken and false is the date is clear.
    """
    found = False
    for curr_event in event_list:
        if str(event) == curr_event:
            found = True

    for subject in tests_list:
        for test in subject:
            if event == test:
                found = True
            
    if found:
        return True
    else:
        return False
    

def the_random_date(start_date, end_date):
    """
    This function generates a random date between two dates
    """
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date


def make_dates_for_tests(classes, start_date):
    """
    This function finds a right date for test and adds it to classes list.
    """
    for one_class in classes:
        valid_date = False
        desired_test_date = the_random_date(start_date, datetime.date(start_date.year, start_date.month, start_date.day)+datetime.timedelta(days=30))
        list_of_events = list_events()
        list_of_tests = list(classes.values())
        while valid_date is False:
            if search_in_events_list(desired_test_date - datetime.timedelta(days=1), list_of_events, list_of_tests) or search_in_events_list(desired_test_date + datetime.timedelta(days=1), list_of_events, list_of_tests) or desired_test_date.weekday() == 5 or search_in_events_list(desired_test_date , list_of_events, list_of_tests):
                desired_test_date = the_random_date(start_date, datetime.date(start_date.year, start_date.month, start_date.day)+datetime.timedelta(days=30))
            else:
                valid_date = True
        classes[one_class].append(desired_test_date)

def First_GUI():
    """
    This function creates a GUI and collects data from the user.
    """
    form = sg.FlexForm('מערכת בית ספר אוטומטית מסך ראשון מתוך ארבעה')

    layout = [
              [sg.Text('הכנס את מספר המקצועות שתרצה לשבץ')],
              [sg.Text('מקצועות:', size=(15, 1)), sg.InputText('0')],
              [sg.Text('שנה לועזית במחצית הראשונה:', size=(15, 1)), sg.InputText('2020')],
              [sg.Text('לפרטים נוספים...')],
              [sg.Text('הווצאפ של רון: +972543182424')],
              [sg.Submit()]
             ]

    button, values = form.Layout(layout).Read()
    return values[0], int(values[1])


def Second_GUI(num_of_classes):
    """
    This function collects the names of the subjects, levels and time extention.
    """
    form = sg.FlexForm('מערכת בית ספר אוטומטית מסך שני מתוך ארבעה')
    layout = [
              [sg.Text('הכנס את שמות המקצועות')],
              [sg.Text('שים לב, לאחר שתלחץ על השליחה התהליך יכול לקחת מספר דקות.')]
              [sg.Text('לפרטים נוספים...')],
              [sg.Text('הווצאפ של רון: +972543182424')],
             ]
    for i in range(int(num_of_classes)):
        layout.append([sg.Text('מקצוע מספר {}'.format(i+1), size=(15, 1)), sg.InputText(''), sg.Checkbox('?יש הקבצות במקצוע זה', size=(16, 1)), sg.Checkbox('יש במקצוע זה הארכת זמן?', size=(20, 1))])
    layout.append([sg.Submit()])
    button, values = form.Layout(layout).Read()
    return values


def Third_GUI(num_of_classes, classes, values):
    """
    This function collects keeper teacher, which levels, location of test, and special needs.
    """
    form = sg.FlexForm('מערכת בית ספר אוטומטית מסך שלישי מתוך ארבעה')
    layout = [
              [sg.Text('אנא מלא את השדות הבאים')],
              [sg.Text('שים לב, לאחר שתלחץ על השליחה התהליך יכול לקחת מספר דקות.')]
             ]
    subjects = []
    for i in classes:
        subjects.append(i)
    for i in range(int(num_of_classes)):
        if values[i*3+1] == True:
            layout.append([sg.Text('{}:'.format(subjects[i]), size=(12, 1)), sg.Text('?איזה הקבצות יש במקצוע הזה'), sg.Checkbox('הקבצה ג', size=(8, 1)),sg.Checkbox('הקבצה ב', size=(8, 1)),sg.Checkbox('הקבצה א', size=(8, 1)),sg.Checkbox('מואץ', size=(6, 1)), sg.Checkbox('?ישנם תלמידים עם צרכים מיוחדים', size=(23, 1)), sg.Text('שמות המורים המשגיחים:', size=(20, 1)), sg.In(default_text='ישראל ישראלי', size=(25, 1)), sg.Text('מיקום/מיקומי המבחן:', size=(13, 1)), sg.In(default_text='כיתת האם', size=(25, 1))])
        else:
            layout.append([sg.Text('{}:'.format(subjects[i]), size=(12, 1)), sg.Checkbox('?ישנם תלמידים עם צרכים מיוחדים', size=(23, 1)), sg.Text('שמות המורים המשגיחים:', size=(20, 1)), sg.In(default_text='ישראל ישראלי', size=(25, 1)), sg.Text('מיקום/מיקומי המבחן:', size=(13, 1)), sg.In(default_text='כיתת האם', size=(25, 1))])
    layout.append([sg.Text('לפרטים נוספים...')])
    layout.append([sg.Text('הווצאפ של רון: +972543182424')])
    layout.append([sg.Submit()])
    button, values = form.Layout(layout).Read()
    return values
    

def Fourth_GUI():
    """
    This function tells the user that the final result came.
    """
    form = sg.FlexForm('מערכת בית ספר אוטומטית מסך אחרון')
    layout = [
              [sg.Text('התהליך הושלם, אנא בדוק את היומן בחשבון הגוגל שלך')],
              [sg.Text('לפרטים נוספים...')],
              [sg.Text('הווצאפ של רון: +972543182424')],
              [sg.Submit()]
             ]
    button = form.Layout(layout).Read()
    
    
def main():
    num_of_classes, curr_year = First_GUI()
    values_from_second_GUI = Second_GUI(num_of_classes)
    classes = {}
    for i in values_from_second_GUI:
        if int(i) == 0:
            classes[values_from_second_GUI[i]] = []
        if int(i)%3 == 0:
            classes[values_from_second_GUI[i]] = []
    print(values_from_second_GUI)
    values_from_third_GUI = Third_GUI(num_of_classes, classes, values_from_second_GUI)
    print(values_from_third_GUI)
    service = get_calendar_service()
    start_first_semester = datetime.date(curr_year, 10, 20)
    end_first_semester = datetime.date(curr_year + 1, 1, 10)
    start_second_semester = datetime.date(curr_year +1, 3, 1)
    end_second_semester = datetime.date(curr_year + 1, 5, 29)

    make_dates_for_tests(classes, start_first_semester)
 
    #This for loop iterates on the classes and sets a date for the second test.
    for two_class in classes:
        valid_second_date = False
        second_test_first_semester = the_random_date(datetime.date(classes.get(two_class)[0].year, classes.get(two_class)[0].month, classes.get(two_class)[0].day)+datetime.timedelta(days=30), datetime.date(end_first_semester.year, end_first_semester.month, end_first_semester.day))
        list_of_tests_num2 = list(classes.values())
        list_of_events_num2 = list_events()
        while valid_second_date is False:
            if search_in_events_list(second_test_first_semester - datetime.timedelta(days=1), list_of_events_num2, list_of_tests_num2) or search_in_events_list(second_test_first_semester + datetime.timedelta(days=1), list_of_events_num2, list_of_tests_num2) or second_test_first_semester.weekday() == 5 or search_in_events_list(second_test_first_semester , list_of_events_num2, list_of_tests_num2):
                second_test_first_semester = the_random_date(datetime.date(classes.get(two_class)[0].year, classes.get(two_class)[0].month, classes.get(two_class)[0].day)+datetime.timedelta(days=30), datetime.date(end_first_semester.year, end_first_semester.month, end_first_semester.day))
            else:
                valid_second_date = True
        classes[two_class].append(second_test_first_semester)
    print(list_of_tests_num2)
    
    #------------------------------handling hakbatzot------------------------------
    hakbatzot = []
    haarahot_zman = []
    for i in range(int(num_of_classes)):
        if values_from_second_GUI[i*3+1] == True:
            hakbatzot.append('1')
        else:
            hakbatzot.append('0')

    for i in range(int(num_of_classes)):
        if values_from_second_GUI[i*3+2] == True:
            haarahot_zman.append('1')
        else:
            haarahot_zman.append('0')

    values_from_third_GUI2 = values_from_third_GUI
    #This for loop fixed format issues for using google calendar api and puts the tests in the calendar.
    iterate = 0
    for curr_class in classes:
        curr_hakbatza = hakbatzot[iterate]
        curr_haarahot_zman = haarahot_zman[iterate]
        the_string = ''
        if curr_hakbatza == '1':
            if values_from_third_GUI2[0] == True:
                the_string += 'הקבצה ג \n'
            if values_from_third_GUI2[1] == True:
                the_string += 'הקבצה ב \n'
            if values_from_third_GUI2[2] == True:
                the_string += 'הקבצה א \n'
            if values_from_third_GUI2[3] == True:
                the_string += 'הקבצה מואצת \n'
            if values_from_third_GUI2[4] == True:
                the_string += 'ישנם תלמידים עם צרכים מיוחדים \n'
            the_string += 'מורה או מורים משגיחים: {} \n'.format(values_from_third_GUI2[5])
            curr_location = 'מיקום המבחן: {} \n'.format(values_from_third_GUI2[6])
            if curr_haarahot_zman == '1':
                the_string += 'במבחן זה יש הארכת זמן \n'
            values_from_third_GUI2 == dict(list(values_from_third_GUI2.items())[7:])
        else:
            if values_from_third_GUI2[0] == True:
                the_string += 'ישנם תלמידים עם צרכים מיוחדים \n'
            the_string += 'מורה או מורים משגיחים: {} \n'.format(values_from_third_GUI2[1])
            curr_location = 'מיקום המבחן: {} \n'.format(values_from_third_GUI2[2])
            if curr_haarahot_zman == '1':
                the_string += 'במבחן זה יש הארכת זמן \n'
            values_from_third_GUI2 == dict(list(values_from_third_GUI2.items())[3:])
        start_1 = classes.get(curr_class)[0]
        start_1_fixed = datetime.datetime(start_1.year, start_1.month, start_1.day, 10)
        start_2 = classes.get(curr_class)[1]
        start_2_fixed = datetime.datetime(start_2.year, start_2.month, start_2.day, 10)
        end_1 = (start_1_fixed + datetime.timedelta(hours=1))
        end_2 = (start_2_fixed + datetime.timedelta(hours=1))
        event_result = service.events().insert(calendarId='primary', body={
           "summary": '{} מבחן ראשון מחצית א'.format(curr_class),
           "location":'{}'.format(curr_location),
           "description": '{}'.format(the_string),
           "start": {"dateTime": start_1_fixed.isoformat(), "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end_1.isoformat(), "timeZone": 'Asia/Kolkata'},
        }
        ).execute()
        event_result_2 = service.events().insert(calendarId='primary', body={
           "summary": '{} מבחן שני מחצית א'.format(curr_class),
           "location":'{}'.format(curr_location),
           "description": '{}'.format(the_string),
           "start": {"dateTime": start_2_fixed.isoformat(), "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end_2.isoformat(), "timeZone": 'Asia/Kolkata'},
        }
        ).execute()
        iterate += 1

    #This for loop empting the list of classes.
    for curr_class_second_semester in classes:
        classes[curr_class_second_semester] = []

    make_dates_for_tests(classes, start_second_semester)

    #This for loop sets dates for second test second semester.
    for two_class in classes:
        valid_second_date = False
        second_test_second_semester = the_random_date(datetime.date(classes.get(two_class)[0].year, classes.get(two_class)[0].month, classes.get(two_class)[0].day)+datetime.timedelta(days=30), datetime.date(end_second_semester.year, end_second_semester.month, end_second_semester.day))
        list_of_tests_num2 = list(classes.values())
        list_of_events_num2 = list_events()
        while valid_second_date is False:
            if search_in_events_list(second_test_second_semester - datetime.timedelta(days=1), list_of_events_num2, list_of_tests_num2) or search_in_events_list(second_test_second_semester + datetime.timedelta(days=1), list_of_events_num2, list_of_tests_num2) or second_test_second_semester.weekday() == 5 or search_in_events_list(second_test_second_semester , list_of_events_num2, list_of_tests_num2):
                second_test_second_semester = the_random_date(datetime.date(classes.get(two_class)[0].year, classes.get(two_class)[0].month, classes.get(two_class)[0].day)+datetime.timedelta(days=30), datetime.date(end_second_semester.year, end_second_semester.month, end_second_semester.day))
            else:
                valid_second_date = True
        classes[two_class].append(second_test_second_semester)
    print(list_of_tests_num2)
    
    #--------custom values------
    values_from_third_GUI3 = values_from_third_GUI
    iterate = 0
    #This for loop fixed format issues for using google calendar api and puts them in tha calendar.
    for curr_class in classes:
        curr_hakbatza = hakbatzot[iterate]
        curr_haarahot_zman = haarahot_zman[iterate]
        the_string = ''
        if curr_hakbatza == '1':
            if values_from_third_GUI3[0] == True:
                the_string += 'הקבצה ג \n'
            if values_from_third_GUI3[1] == True:
                the_string += 'הקבצה ב \n'
            if values_from_third_GUI3[2] == True:
                the_string += 'הקבצה א \n'
            if values_from_third_GUI3[3] == True:
                the_string += 'הקבצה מואצת \n'
            if values_from_third_GUI3[4] == True:
                the_string += 'ישנם תלמידים עם צרכים מיוחדים \n'
            the_string += 'מורה או מורים משגיחים: {} \n'.format(values_from_third_GUI3[5])
            curr_location = 'מיקום המבחן: {} \n'.format(values_from_third_GUI3[6])
            if curr_haarahot_zman == '1':
                the_string += 'במבחן זה יש הארכת זמן \n'
            values_from_third_GUI3 == dict(list(values_from_third_GUI3.items())[7:])
        else:
            if values_from_third_GUI3[0] == True:
                the_string += 'ישנם תלמידים עם צרכים מיוחדים \n'
            the_string += 'מורה או מורים משגיחים: {} \n'.format(values_from_third_GUI3[1])
            curr_location = 'מיקום המבחן: {} \n'.format(values_from_third_GUI3[2])
            if curr_haarahot_zman == '1':
                the_string += 'במבחן זה יש הארכת זמן \n'
            values_from_third_GUI3 == dict(list(values_from_third_GUI3.items())[3:])
        start_1 = classes.get(curr_class)[0]
        start_1_fixed = datetime.datetime(start_1.year, start_1.month, start_1.day, 10)
        start_2 = classes.get(curr_class)[1]
        start_2_fixed = datetime.datetime(start_2.year, start_2.month, start_2.day, 10)
        end_1 = (start_1_fixed + datetime.timedelta(hours=1))
        end_2 = (start_2_fixed + datetime.timedelta(hours=1))
        event_result = service.events().insert(calendarId='primary', body={
           "summary": '{} מבחן ראשון מחצית ב'.format(curr_class),
           "location":'{}'.format(curr_location),
           "description": '{}'.format(the_string),
           "start": {"dateTime": start_1_fixed.isoformat(), "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end_1.isoformat(), "timeZone": 'Asia/Kolkata'},
        }
        ).execute()
        event_result_2 = service.events().insert(calendarId='primary', body={
           "summary": '{} מבחן שני מחצית ב'.format(curr_class),
           "location":'{}'.format(curr_location),
           "description": '{}'.format(the_string),
           "start": {"dateTime": start_2_fixed.isoformat(), "timeZone": 'Asia/Kolkata'},
           "end": {"dateTime": end_2.isoformat(), "timeZone": 'Asia/Kolkata'},
        }
        ).execute()

    Fourth_GUI()
        
        

if __name__ == '__main__':
   main()
