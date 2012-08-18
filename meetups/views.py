from . import app, meetup, mongo
from flask import render_template, redirect, url_for, request, session, flash
from flask.ext.login import login_required, login_user, logout_user

from .models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/have/')
def have():
    return render_template('have.html')


@app.route('/login/', methods=('GET', 'POST'))
def login():
    return meetup.authorize(callback=url_for('login_meetup_return'))


@app.route('/login/meetup/return/', methods=('GET',))
@meetup.authorized_handler
def login_meetup_return(oauth_response):
    next_url = url_for('index')
    if oauth_response is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['meetup_token'] = (
        oauth_response['oauth_token'],
        oauth_response['oauth_token_secret']
    )
    session['member_id'] = oauth_response['member_id']

    user = User(_id=oauth_response['member_id'])
    user.refresh()
    user.save()
    login_user(user, remember=True)

    flash('You are now signed in!')
    return redirect(next_url)


@app.route('/logout/')
def logout():
    session.pop('meetup_token', None)
    session.pop('meetup_member_id', None)
    session.pop('user_name', None)
    logout_user()
    return redirect(url_for('.index'))


@app.route('/need/')
def need():
    return render_template('need.html')


@meetup.tokengetter
def get_twitter_token():
    return session.get('meetup_token')
