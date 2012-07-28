from . import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/have/')
def have():
    return render_template('have.html')


@app.route('/need/')
def need():
    return render_template('need.html')
