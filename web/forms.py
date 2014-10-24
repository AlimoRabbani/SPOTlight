__author__ = 'Alimohammad'

from wtforms import Form, StringField, PasswordField, validators, BooleanField


class LoginForm(Form):
    email = StringField('Email Address', [validators.email(message=u'Invalid email address')])
    password = PasswordField('Password', [validators.DataRequired()])
    remember = BooleanField('Remember Me')