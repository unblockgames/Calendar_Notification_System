# Calendar_Notification_System

WHATS NEW? 

*Implemented multi-notification support with the use of <notify> tag in description.
  
  In the description of any event you can add a <notify></notify> tag and append a list of minutes prior to the event you'd like to be notified.
  for example <notify>50,40,30,5,1</notify> would alert you 50 minutes, 40 minutes, 30 minutes, 5 minutes and 1 minute before an event.

This is a custom implementation of a phone call notification system based on google calendar. The whole point of this project is to make an ADHD person such as myself not miss appointments anymore because the normal notifications provided by google calendar are insufficient. Furthermore, I do not wish to use Zapier or a paid SMS notification tool. I prefer a phone call but this software could easily send an SMS instead.

In order to use this software, youll need a service account with Google and also youll need an account with Twilio.

As the project progresses, I may decide to make this software handle multiple users and more dynamic and flexible options. This is a simple python script, designed to be executed on a regular interval using cron. Keep in mind that your cron will need full disk access for this project to work.

The overall concept is simple. Call google calendar, figure out when your upcoming events are and schedule a cron job to call the twilio api (which in turn calls you)

Enjoy.

INITIAL SETUP...

the calnotify.py is the entry point file in this application. The general usage of this is to adjust the config in accordance with your own information, then run the script. The only thing you need to adjust in the code would be at the beginning of the calnotify.py and the twiliocall.py. The line that opens the config file.

once the config file is successfully opened, the remainder of the program will pull needed info from the config. This is will adjusted in the future so as to not need any code changes to run.

I have also included a Dockerfile that as of now, has been tested and works. If you know how to build a docker image and run it, this should work like a charm.

I will put effort into making this a more hosted and easy to use service in the future.
