# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm,UpdateAccountForm
from app.base.models import User
from app.base.util import verify_pass, hash_pass
import re 

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/error-<error>')
def route_errors(error):
    return render_template('errors/{}.html'.format(error))

## Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        # read form data
        username = request.form['username']
        password = request.form['password']
        # Locate user
        user = User.query.filter_by(username=username).first()
        # Check the password
        if user and verify_pass( password, user.password):
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))
        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)
    if not current_user.is_authenticated:
        return render_template( 'login/login.html',form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:
        username  = request.form['username']
        email     = request.form['email'   ]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'login/register.html', msg='Username already registered', form=create_account_form)
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'login/register.html', msg='Email already registered', form=create_account_form)
        email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if not (re.search(email_regex,email)):
            return render_template( 'login/register.html', msg='Invalid Email', form=create_account_form)
        # else we can create the user
        user = User(**request.form)
        user.refreshrate=5
        user.maxpackets = 200
        user.alerts = True
        db.session.add(user)
        db.session.commit()
        return render_template( 'login/register.html', msg='User created please <a href="/login">login</a>', form=create_account_form)
    else:
        return render_template( 'login/register.html', form=create_account_form)

@blueprint.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    login_form = LoginForm(request.form)
    if current_user.is_authenticated:
        update_account_form = UpdateAccountForm(request.form)
        if 'update_email' in request.form:
            email = request.form['email']
            email_regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            if email and re.search(email_regex,email):
                current_user.email = email
                db.session.commit()
                return render_template('login/profile.html',msg='Email updated',form=update_account_form,color='lime')
            else:
                return render_template('login/profile.html',msg='Invalid Email',form=update_account_form,color='red')
        elif 'update_password' in request.form:
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            verify_new_password = request.form['verify_new_password']
            if old_password and not verify_pass( old_password, current_user.password) : 
                return render_template('login/profile.html',msg='Current password is not correct',form=update_account_form,color='red')
            if verify_pass( old_password, current_user.password) and new_password and verify_new_password  \
                and old_password and old_password==new_password:
                return render_template('login/profile.html',msg='Insert a different new password',form=update_account_form,color='red')
        
            if not( verify_pass( old_password, current_user.password) and new_password and verify_new_password \
                 and new_password==verify_new_password and new_password==verify_new_password):
                return render_template('login/profile.html',msg='Invalid new password',form=update_account_form,color='red')
            current_user.password = hash_pass(new_password)
            db.session.commit()
            return render_template('login/profile.html',msg='User updated',form=update_account_form,color='lime')
        return render_template('login/profile.html',form=update_account_form)
    return render_template( 'login/login.html',form=login_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500