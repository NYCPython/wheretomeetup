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

RequestForSpaceInitial = namedtuple('RequestForSpaceInitial',
                                    ['name', 'email', 'phone', 'body'])
