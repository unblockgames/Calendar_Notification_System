import sqlite3
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import json

with open('/Users/jasoncasey/Documents/JasonCodeBook/Calendar_Notification_System/config.json', 'r') as f:
    config = json.load(f)
# Your Account SID from twilio.com/console
account_sid = config['Twilio']['account_sid']
# Your Auth Token from twilio.com/console
auth_token = config['Twilio']['auth_token']
client = Client(account_sid, auth_token)
# SQLite database connection object
con = sqlite3.connect(
    '/Users/jasoncasey/Documents/JasonCodeBook/Calendar_Notification_System/example.db')
# SQLite database cursor object
cur = con.cursor()


def callPerson(id):
    cur.execute("SELECT * FROM events WHERE googleId='{}'".format(id))
    event = cur.fetchone()
    twilio_response = VoiceResponse()
    twilio_response.pause(1)
    twilio_response.say(
        "Hey Diveej! I am calling to remind you about, {}.".format(event[3]))
    twilio_response.pause(1)
    twilio_response.say("It's coming up in 1 hour. Have a good day!")
    call = client.calls.create(
        twiml=twilio_response,
        to='+18176293724',
        from_='+18175009328',
    )
    # CALL CLEANUP FUNCTION
    con.close()
    return
