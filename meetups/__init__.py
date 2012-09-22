# Copyright (c) 2012, The NYC Python Meetup
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import os.path

import bugsnag
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

app.config['BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT'] = conf('BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT')
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

app.config['MONGO_HOST'] = conf('MONGOHQ_URL', None)
mongo = PyMongo(app)

sendgrid_api = sendgrid.Sendgrid(
    username=conf('SENDGRID_USERNAME'),
    password=conf('SENDGRID_PASSWORD'),
    secure=True,
)

if conf('BUGSNAG_API_KEY'):
    bugsnag.configure(
        api_key=conf('BUGSNAG_API_KEY'),
        release_stage=conf('BUGSNAG_RELEASE_STAGE', 'development'),
        notify_release_stages=['production'],
        auto_notify=False,
        use_ssl=True,
        project_root=os.path.dirname(os.path.dirname(__file__)),
        # project_version=
    )

from .models import login_manager
login_manager.setup_app(app)

from . import views
from . import filters
