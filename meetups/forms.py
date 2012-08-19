from collections import namedtuple
from wtforms import Form, TextField, TextAreaField, BooleanField, HiddenField, validators


class UserProfileForm(Form):
    _id = HiddenField()

    email = TextField('Email', [validators.Email()])
    phone = TextField('Phone')


class VenueClaimForm(Form):
    _id = HiddenField()

    name = TextField('Contact Name', [validators.Required()])
    email = TextField('Contact Email',
        [validators.Required(), validators.Email()])
    phone = TextField('Contact Phone', [validators.Required()])

    confirm = BooleanField('I hereby certify that this space belongs to me',
        [validators.Required()])


class RequestForSpaceForm(Form):
    name = TextField('Your Name', [validators.Required()])
    email = TextField('Your Email',
        [validators.Required(), validators.Email()])
    phone = TextField('Your Phone', [validators.Required()])

    body = TextAreaField('Message to Hosts', [validators.Required()])

from datetime import datetime
import pytz
import re

_RequestForSpaceInitial = namedtuple('RequestForSpaceInitial',
                                     ['name', 'email', 'phone', 'body'])

def RequestForSpaceInitial(user, event, group):
    initial = {
        'name': user.name,
        'email': getattr(user, 'email', ''),
        'phone': getattr(user, 'phone', ''),
        'body': """Hey there {{host}},

My name is %(user_name)s, and I'm interested in hosting an upcoming event for %(group_name)s at your location, {{venue_name}}. Our event, %(event_name)s on %(event_date)s, and will be about %(event_size)s folks. I hope you can host us!

Thanks,
- %(user_name)s"""}

    if event.time:
        # TODO: look up timezone for user based on location
        timezone = 'America/New_York'
        event_date = datetime.utcfromtimestamp(event.time / 1000)
        event_date = pytz.timezone(timezone).localize(event_date)
        event_date = event_date.strftime('%A %B %d, %Y at %I:%M %p')
        event_date = re.sub(r'0(\d,)', r'\1', event_date)
    else:
        event_date = '(you have not scheduled your event, but hosts will want to know when to expect you)'

    initial['body'] = initial['body'] % {
        'user_name': user.name,
        'group_name': group.name,
        'event_name': event.name,
        'event_date': event_date,
        'event_size': getattr(event, 'rsvp_limit', '???'),
    }

    return _RequestForSpaceInitial(**initial)

