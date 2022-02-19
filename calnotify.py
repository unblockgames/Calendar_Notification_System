from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from crontab import CronTab
import json
import sqlite3
import hashlib as h
from datetime import datetime, timedelta
from config import CONFIG

# Developtment

DIRECTORY = CONFIG['Directories']['codebase']
PYTHON3 = CONFIG['Directories']['python3']
# TODO: Add a way for this to be dynamic on a per event basis!
minutesBefore = int(CONFIG['minutesBefore'])

# SQLite database connection object
con = sqlite3.connect(DIRECTORY + '/calendar.db')
# SQLite database cursor object
cur = con.cursor()

SCOPES = ['https://www.googleapis.com/auth/calendar']


def scheduleNotification(data):
    try:
        # create the py file to be executed
        f = open(
            DIRECTORY + '/scripts/{}.py'.format(data[0]), 'w')
        code = "import sys\nsys.path.append(\'" + DIRECTORY + "\')\nfrom twiliocall import callPerson\ncallPerson(\'{}\')".format(
            data[0])
        f.write(code)
        f.close()
        # create cron job
        command = PYTHON3 + ' ' + DIRECTORY + \
            '/scripts/{}.py >> '.format(data[0]) + \
            CONFIG['Directories']['cron_output'] + ' 2>&1'
        my_cron = CronTab(user=CONFIG['User'])
        job = my_cron.new(command=command)
        # Set up time for notification to happen
        dateObj = json.loads(data[1])
        if 'dateTime' in dateObj:
            timezoneSign = dateObj['dateTime'][19]
            timezoneHour = int(dateObj['dateTime'][20:22])
            timezoneMinute = int(dateObj['dateTime'][23:25])
            startTime = datetime.strptime(
                dateObj['dateTime'][0: 16], "%Y-%m-%dT%H:%M")
            print(startTime)
        elif 'date' in dateObj:
            print("Date has no time associated with it. It is a whole day event. Notifications for Whole day events are not implemented yet!")
            # startTime = datetime.strptime(
            #    dateObj['date'], "%Y-%m-%d")
            return
        else:
            print(
                "Error! Neither \"dateTime\" or \"date\" keys were found in the event dictionary.")
        # Convert local time to UTC
        if timezoneSign == '-':
            startTime = startTime + \
                timedelta(hours=timezoneHour, minutes=timezoneMinute)
        elif timezoneSign == '+':
            startTime = startTime - \
                timedelta(hours=timezoneHour, minutes=timezoneMinute)
        else:
            print("Timezone sign error")
        hourBefore = timedelta(minutes=-minutesBefore) + startTime
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


def insertIntoDatabase(event):
    try:
        # add event to table
        # Insert a row of data
        if 'description' not in event:
            event['description'] = "null"
        if 'location' not in event:
            event['location'] = "null"
        if 'attendees' not in event:
            event['attendees'] = "null"
        sqlStatement = "INSERT INTO events VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', false, NULL, '{}')".format(event['id'], json.dumps(
            event['start']), json.dumps(event['end']), event['summary'].replace("'", ""), event['description'], event['location'], json.dumps(event['attendees']), eventHash)
        cur.execute(sqlStatement)
        con.commit()
    except:
        pass
    return


# Grab all the upcoming events on the google calendar
secret_file = CONFIG['Directories']['codebase'] + \
    '/service_account_secret.json'
credentials = service_account.Credentials.from_service_account_file(
    secret_file, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)
calendar = service.calendars().get(
    calendarId=CONFIG['Google']['calendar_id']).execute()
timeMin = (datetime.now() - timedelta(days=1)
           ).strftime("%Y-%m-%dT%H:%M:00-06:00")
timeMax = (datetime.now() + timedelta(days=+30)
           ).strftime("%Y-%m-%dT%H:%M:00-06:00")
events = service.events().list(calendarId=CONFIG['Google']['calendar_id'],
                               timeMin=timeMin, timeMax=timeMax).execute()

# Check to see if the events in google calendar exist in the databse.
# If they dont, add them or if they are different, update them.

for event in events['items']:
    jsonEvent = json.dumps(event)
    eventHash = h.sha256(jsonEvent.encode('utf-8')).hexdigest()
    cur.execute(
        "SELECT event_hash FROM events WHERE googleId='{}'".format(event['id']))
    fetched = cur.fetchall()
    if len(fetched) > 0:
        print("Event \"{}\" already exists!".format(event['summary']))
        if fetched[0][0] != eventHash:
            print("Hashes are different! Updating event details NOT YET IMPLEMENTED!!")
            # TODO: Implement updating of details when hashes don't match
            # REMOVE CRON JOB
            my_cron = CronTab(user=CONFIG['User'])
            iter = my_cron.find_command(event['id'])
            for job in iter:
                my_cron.remove(job)
            my_cron.write()
            # DELETE OLD ENTRY FROM DATABASE
            sqlStatement = "DELETE FROM events WHERE googleId='{}'".format(
                event['id'])
            # INSET NEW ENTRY INTO DATABASE
            cur.execute(sqlStatement)
            con.commit()
            insertIntoDatabase(event)

    else:
        insertIntoDatabase(event)
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
