"""Server"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, session, flash)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Update, connect_to_db, db

from datetime import datetime

import os

app = Flask(__name__)

#reminder: need to input "source secret.sh" in shell to use
app.secret_key = os.environ["SECRET_KEY"]

#so that error raised if jinja tries to reference an undefined variable
app.jinja_env.undefined = StrictUndefined
#so that app autoreloads in debug mode (specification needed because of above)
app.jinja_env.auto_reload = True

#routes here

if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(port=5000)