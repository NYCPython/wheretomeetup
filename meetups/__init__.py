from flask import Flask
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

from . import views
