# Calendar_Notification_System

This is a custom implementation of a phone call notification system based on google calendar. The whole point of this project is to make an ADHD such as myself not miss appointments anymore because the normal notifications provided by google calendar are insufficient. Furthermore, I do not wish to use Zapier or a paid SMS notification tool. I prefer a phone call but this software could easily send an SMS instead.

In order to use this software, youll need a service account with Google and also youll need an account with Twilio.

As the project progresses, I may decide to make this software handle multiple users and more dynamic and flexible options. This is a simple python script, designed to be executed on a regular interval using cron. Keep in mind that your cron will need full disk access for this project to work.

The overall concept is simple. Call google calendar, figure out when your upcoming events are and schedule a cron job to call the twilio api (which in turn calls you)

Enjoy.
