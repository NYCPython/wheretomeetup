import os
DEBUG = os.getenv('DEBUG') == 'True'

from meetups import app
app.run(debug=DEBUG)
