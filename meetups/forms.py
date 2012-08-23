from collections import namedtuple
from wtforms import (Form, validators, TextField, TextAreaField, BooleanField,
    IntegerField, HiddenField)


class UserProfileForm(Form):
    _id = HiddenField()

    email = TextField('Email', [validators.Email()])
    phone = TextField('Phone')


class VenueEditForm(Form):
    _id = HiddenField()

    contact_name = TextField('Contact Name', [validators.Required()])
    contact_email = TextField('Contact Email',
        [validators.Required(), validators.Email()])
    contact_phone = TextField('Contact Phone', [validators.Required()])

    capacity = IntegerField('Maximum Capacity',
        [validators.NumberRange(min=0)], default=0)


class VenueClaimForm(VenueEditForm):
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

My name is %(user_name)s, and I'm interested in hosting an upcoming event for %(group_name)s at your location, {{venue_name}}. Our event, "%(event_name)s" on %(event_date)s will attract about %(event_size)s folks. If you can host us, please reply and let me know!

Thanks,
- %(user_name)s"""}

    if getattr(event, 'time', False):
        # TODO: look up timezone for user based on location
        timezone = 'America/New_York'
        event_date = datetime.utcfromtimestamp(event.time / 1000)
        event_date = pytz.timezone(timezone).localize(event_date)
        event_date = event_date.strftime('%A %B %d, %Y at %I:%M %p')
        event_date = re.sub(r'0(\d,)', r'\1', event_date)
    else:
        event_date = '[event date]'

    initial['body'] = initial['body'] % {
        'user_name': user.name,
        'group_name': group.name,
        'event_name': event.name,
        'event_date': event_date,
        'event_size': getattr(event, 'rsvp_limit', '[RSVP limit]'),
    }

    return _RequestForSpaceInitial(**initial)

