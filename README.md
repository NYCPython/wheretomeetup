[![Build Status](https://secure.travis-ci.org/NYCPython/wheretomeetup.png?branch=develop)](http://travis-ci.org/NYCPython/wheretomeetup)

# Meetups

A site for connecting groups and locations. More information coming soon.


## Setup Notes

You will need to create an application at Meetup.com at
http://www.meetup.com/meetup_api/oauth_consumers/create/. Create a file at
the root of this repository named `secrets.cfg`, with the contents:

    MEETUP_OAUTH_CONSUMER_KEY = 'your-meetup-application-key'
    MEETUP_OAUTH_CONSUMER_SECRET = 'your-meetup-application-secret'

To send email, you will need a [free SendGrid
account](http://sendgrid.com/user/signup). Once you have signed up and your
account is activated, go to [the credentials management
page](https://sendgrid.com/credentials), and add a new username and
password. Be sure to check the "API" and "Mail" (but not "Web") permissions
checkboxes. Add the username and password to `secrets.cfg` like:

    SENDGRID_USERNAME = 'your-new-username'
    SENDGRID_PASSWORD = 'your-new-password'

## Geospatial data

All geospatial data should be stored as an array formatted
`[longitude, latitude]`. A 2d index should be created on the field.
