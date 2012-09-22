import os

import sendgrid
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.oauth import OAuth
from flask.ext.pymongo import PyMongo

app = Flask(__name__)

try:
    app.config.from_pyfile('../secrets.cfg')
except IOError:
    # app.log.warn('could not load secrets.cfg')
    pass

def conf(key, default=''):
    """Helper to load a configuration from `app.config`, if it
    exists, or from `os.environ` (and saving into `app.config`).
    """
    if key in app.config:
        return app.config[key]
    elif key in os.environ:
        app.config[key] = os.environ[key]
        return app.config[key]
    return default

app.secret_key = conf('FLASK_SECRET_KEY', 'Bn1dcC2QDWXgtj')

Bootstrap(app)

oauth = OAuth()
meetup = oauth.remote_app('meetup',
    base_url='https://api.meetup.com/',
    request_token_url='https://api.meetup.com/oauth/request/',
    access_token_url='https://api.meetup.com/oauth/access/',
    authorize_url='http://www.meetup.com/authorize/',
    consumer_key=conf('MEETUP_OAUTH_CONSUMER_KEY'),
    consumer_secret=conf('MEETUP_OAUTH_CONSUMER_SECRET'),
)

app.config['MONGO_URI'] = conf('MONGOHQ_URL', None)
mongo = PyMongo(app)

sendgrid_api = sendgrid.Sendgrid(
    username=conf('SENDGRID_USERNAME'),
    password=conf('SENDGRID_PASSWORD'),
    secure=True,
)

from .models import login_manager
login_manager.setup_app(app)

from . import views
