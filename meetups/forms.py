from wtforms import Form, TextField, PasswordField, validators


class LoginForm(Form):
    email = TextField('Email', (validators.Email(),))
    password = PasswordField('Password', (validators.Required(),))
