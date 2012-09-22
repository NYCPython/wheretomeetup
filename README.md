[![Build Status](https://secure.travis-ci.org/NYCPython/wheretomeetup.png?branch=develop)](http://travis-ci.org/NYCPython/wheretomeetup)

# Meetups

A site for connecting groups and locations. More information coming soon.


## Setup Notes

You will need to [create an application at
Meetup.com](http://www.meetup.com/meetup_api/oauth_consumers/create/). Be sure not to
enter a Redirect URI, as this will cause Meetup to send OAuth 2.0 responses
(WhereToMeetup use OAuth 1.0a).

Create a file at the root of this repository named `secrets.cfg`, with the
contents:

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

## Running the Test Suite

If you're going to be contributing to WhereToMeetup, you're going to want to
run its test suite as you work.

If you just want to run the tests quickly, you can just run

    YourFavoriteTestRunner tests

on the `tests` package at the root of the repository. Before you send a pull
request or if you want to exactly imitate the test setup that the other
developers are working with though, you should instead use
[tox](http://tox.readthedocs.org/en/latest/index.html) by running

    pip install tox
    tox

in the root of the repository, which will run the test suite on all of the
supported environments.

## Release Notes

To perform a release to Heroku:

1. Merge `develop` into the release branch (named after a version series,
like `0.9.x`)
2. If all tests pass on the release branch, merge the release branch to
`master`
3. Create a new version number as a commit on `master`, and create a tag
with that version
4. Deploy to Heroku with `git push heroku master`
5. Push the release branch, tags, and `master` back to Github.
