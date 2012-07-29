from . import app
from flask import render_template, redirect, url_for, request
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
