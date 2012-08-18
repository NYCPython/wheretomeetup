#######
Meetups
#######

A site for connecting groups and locations. More information coming soon.


===========
Setup Notes
===========

You will need to create an application at Meetup.com at
http://www.meetup.com/meetup_api/oauth_consumers/create/. Create a file at
the root of this repository named ``secrets.cfg``, with the contents::

    MEETUP_OAUTH_CONSUMER_KEY = 'your-meetup-application-key'
    MEETUP_OAUTH_CONSUMER_SECRET = 'your-meetup-application-secret'

