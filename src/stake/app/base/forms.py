# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField ,IntegerField
from wtforms.validators import DataRequired

## login and registration
class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login'   , validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login'        , validators=[DataRequired()])

class CreateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[DataRequired()])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired()])
    password = PasswordField('Password' , id='pwd_create'      , validators=[DataRequired()])

class UpdateAccountForm(FlaskForm):
    email    = TextField('Email'        , id='update_email'    , validators=[DataRequired()])
    old_password = PasswordField('Old Password' , id='old_pwd'      , validators=[DataRequired()])
    new_password = PasswordField('New Password' , id='update_pwd'      , validators=[DataRequired()])
    verify_new_password = PasswordField('Verify New Password' , id='verify_update_pwd'      , validators=[DataRequired()])