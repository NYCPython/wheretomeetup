from . import app, meetup
from flask import render_template, redirect, url_for, request, session, flash
from flask.ext.login import login_required, logout_user

from .forms import LoginForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/have/')
def have():
    return render_template('have.html')


@app.route('/login/', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('.index'))
    return render_template('login.html', form=form)


@app.route('/login/meetup/', methods=('GET',))
def login_meetup():
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
    session['meetup_member_id'] = oauth_response['member_id']

    response = meetup.get('/2/member/%s' % session['meetup_member_id'])
    session['user_name'] = response.data['name']
    session['locale'] = response.data['lang']
    session['latlong'] = (response.data['lat'], response.data['lon'])

    flash('You are now signed in!')
    return redirect(next_url)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/need/')
def need():
    return render_template('need.html')

@meetup.tokengetter
def get_twitter_token():
    return session.get('meetup_token')
