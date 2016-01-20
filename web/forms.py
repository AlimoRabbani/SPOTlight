__author__ = 'Alimohammad'

from wtforms import Form, StringField, PasswordField, validators, BooleanField

from flask import current_app

import urllib
import urllib2
import json

class LoginForm(Form):
    email = StringField('Email Address', [validators.email(message=u'Invalid email address')])
    password = PasswordField('Password', [validators.DataRequired(message=u'Password required')])
    remember = BooleanField('Remember Me')

class ForgotPasswordForm(Form):
    email = StringField('Email Address', [validators.email(message=u'Invalid email address')])

class ChangePassowrdForm(Form):
    password = PasswordField('New Password', [validators.DataRequired(message=u'You must enter a new password.')])
    confirm = PasswordField('Repeat Password', [validators.DataRequired(message=u'You must confirm the new password.'),
                                                validators.EqualTo('password', message='Passwords do not match')])

def recaptcha_check(recaptcha_response):
    url = "https://www.google.com/recaptcha/api/siteverify"
    values = {'secret': current_app.config["custom_config"]["g-recaptcha-secret"], 'response': recaptcha_response}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data['success']