from flask import Flask
from flask.ext.bootstrap import Bootstrap
from .models import login_manager

app = Flask(__name__)
app.secret_key = 'Bn1dcC2QDWXgtj'

Bootstrap(app)
login_manager.setup_app(app)

from . import views
