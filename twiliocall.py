import sqlite3
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import json
from config import CONFIG

DIRECTORY = CONFIG['Directories']['codebase']

# Your Account SID from twilio.com/console
account_sid = CONFIG['Twilio']['account_sid']
# Your Auth Token from twilio.com/console
auth_token = CONFIG['Twilio']['auth_token']
client = Client(account_sid, auth_token)
# SQLite database connection object
con = sqlite3.connect(DIRECTORY + '/calendar.db')
# SQLite database cursor object
cur = con.cursor()


def callPerson(id):
    cur.execute("SELECT * FROM events WHERE googleId='{}'".format(id))
    event = cur.fetchone()
    twilio_response = VoiceResponse()
    twilio_response.pause(1)
    twilio_response.say(
        "Hey Jason! I am calling to remind you about, {}.".format(event[3]))
    twilio_response.pause(1)
    twilio_response.say("It's coming up in 1 hour. Have a good day!")
    call = client.calls.create(
        twiml=twilio_response,
        to='+18173081906',
        from_='+18175009328',
    )
    # CALL CLEANUP FUNCTION
    con.close()
    return
