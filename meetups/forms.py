from wtforms import Form, TextField, BooleanField, HiddenField, validators


class VenueClaimForm(Form):
    _id = HiddenField()

    name = TextField('Contact Name', [validators.Required()])
    email = TextField('Contact Email',
        [validators.Required(), validators.Email()])
    phone = TextField('Contact Phone', [validators.Required()])

    confirm = BooleanField('I hereby certify that this venue belongs to me',
        [validators.Required()])
