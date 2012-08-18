from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.oauth import OAuth
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'Bn1dcC2QDWXgtj'

try:
    app.config.from_pyfile('../secrets.cfg')
except IOError:
    # app.log.warn('could not load secrets.cfg')
    pass

Bootstrap(app)

oauth = OAuth()
meetup = oauth.remote_app('meetup',
    base_url='https://api.meetup.com/',
    request_token_url='https://api.meetup.com/oauth/request/',
    access_token_url='https://api.meetup.com/oauth/access/',
    authorize_url='http://www.meetup.com/authorize/',
    consumer_key=app.config.get('MEETUP_OAUTH_CONSUMER_KEY', ''),
    consumer_secret=app.config.get('MEETUP_OAUTH_CONSUMER_SECRET', ''),
)

mongo = PyMongo(app)

from .models import login_manager
login_manager.setup_app(app)

from . import views
