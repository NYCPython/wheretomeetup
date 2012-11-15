# Copyright (c) 2012, The NYC Python Meetup
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from collections import namedtuple
from wtforms import (Form, validators, TextField, TextAreaField, BooleanField,
    IntegerField, HiddenField)


class UserProfileForm(Form):
    """Edit contact information associated with a user."""
    _id = HiddenField()

    email = TextField('Email', [validators.Email()])
    phone = TextField('Phone')


class VenueEditForm(Form):
    """Edit information associated with a venue.

    The contact information and capacity are required. All of the fields that
    make up the questionnaire portion of the form, however, are optional.
    """
    _id = HiddenField()

    contact_name = TextField('Contact Name', [validators.Required()])
    contact_email = TextField('Contact Email',
        [validators.Required(), validators.Email()])
    contact_phone = TextField('Contact Phone', [validators.Required()])

    capacity = IntegerField('Maximum Capacity',
        [validators.NumberRange(min=0)])

    # Optional questionnaire fields
    need_names = BooleanField('A list of names is required ahead of time.')
    food = BooleanField('Food can be provided by the host.')
    av = BooleanField('There is a screen and/or projector.')
    chairs = BooleanField('There is sufficient seating.')
    instructions = TextAreaField('Special instructions '
        '(e.g., take a particular evelvator, use a specific door)')


class VenueClaimForm(VenueEditForm):
    """Extends the :class:`~meetup.forms.VenueEditForm` to add a confirmation
    field.
    """
    confirm = BooleanField('I hereby certify that this space belongs to me',
        [validators.Required()])


class VenueSearchForm(Form):
    """Search for a venue."""
    name = TextField('Venue Name', [validators.Required()])

    use_current_location = BooleanField('Find venues near me')

    longitude = HiddenField()
    latitude = HiddenField()

    # TODO: Move this to a custom OptionalIfNot validator after OptionalIf
    # has been merged.
    def validate_use_current_location(form, field):
        """Validate that the geolocation has been included for a form
        specifying to use the current location.
        """
        if field.data:
            if not (form.longitude.data or form.latitude.data):
                raise validators.ValidationError('It appears you have blocked '
                                                 'this site from accessing '
                                                 'your location.')


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
