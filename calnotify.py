from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from crontab import CronTab
import json
import sqlite3
from datetime import datetime, timedelta

# SQLite database connection object
con = sqlite3.connect('example.db')
# SQLite database cursor object
cur = con.cursor()

SCOPES = ['https://www.googleapis.com/auth/calendar']


def scheduleNotification(data):
    try:
        # create the py file to be executed
        f = open(
            '/Users/jasoncasey/Documents/JasonCodeBook/Calendar_Notification_System/{}.py'.format(data[0]), 'w')
        code = "import sys\nsys.path.append(\'/Users/jasoncasey/Documents/JasonCodeBook/Calendar_Notification_System\')\nfrom twiliocall import callPerson\ncallPerson(\'{}\')".format(
            data[0])
        f.write(code)
        f.close()
        # create cron job
        command = '/Users/jasoncasey/.local/share/virtualenvs/Calendar_Notification_System-lf8G-LEN/bin/python3 /Users/jasoncasey/Documents/JasonCodeBook/Calendar_Notification_System/{}.py >> /tmp/log/stdout.log 2>&1'.format(
            data[0])
        my_cron = CronTab(user='jasoncasey')
        job = my_cron.new(command=command)
        # Set up time for notification to happen

        startTime = datetime.strptime(json.loads(
            data[1])['dateTime'][0: 16], "%Y-%m-%dT%H:%M")
        hourBefore = timedelta(hours=-1) + startTime
        job.minute.on(startTime.minute)
        job.hour.on(hourBefore.hour)
        job.month.on(startTime.month)
        job.day.on(startTime.day)
        my_cron.write()
        # change database
        cur.execute(
            "UPDATE events SET scheduled=TRUE WHERE googleId='{}'".format(data[0]))
        con.commit()
        return True
    except:
        return False


secret_file = './service_account_secret.json'
credentials = service_account.Credentials.from_service_account_file(
    secret_file, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)
calendar = service.calendars().get(calendarId='unblockgames@gmail.com').execute()
events = service.events().list(calendarId='unblockgames@gmail.com',
                               timeMin='2022-02-07T00:00:00-06:00', timeMax='2022-02-28T00:00:00-06:00').execute()

# Perform a query and if no event, add event
for event in events['items']:
    cur.execute(
        "SELECT googleId FROM events WHERE googleId='{}'".format(event['id']))
    fetched = cur.fetchall()
    if len(fetched) > 0:
        print("Event \"{}\" already exists!".format(event['summary']))
    else:
        # add event to table
        # Insert a row of data
        if 'description' not in event:
            event['description'] = "null"
        if 'location' not in event:
            event['location'] = "null"
        if 'attendees' not in event:
            event['attendees'] = "null"
        sqlStatement = "INSERT INTO events VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', false, NULL)".format(event['id'], json.dumps(
            event['start']), json.dumps(event['end']), event['summary'].replace("'", ""), event['description'], event['location'], json.dumps(event['attendees']))
        cur.execute(sqlStatement)
        con.commit()

# For each event in the database, check to see which ones have a scheduled notification (phone call)
# For all events that dont have a scheduled notification, schedule the notification

cur.execute("SELECT * FROM events WHERE scheduled=False")
for row in cur.fetchall():
    if scheduleNotification(row):
        print("{} Scheduled Successfully!".format(row[3]))
    else:
        print("{} Failed to Schedule!".format(row[3]))

con.close()
print("Completed")
