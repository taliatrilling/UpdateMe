"""Server"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, session, flash)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Update, connect_to_db, db

import os

app = Flask(__name__)

#reminder: need to input "source secret.sh" in shell to use
app.secret_key = os.environ["SECRET_KEY"]

#so that error raised if jinja tries to reference an undefined variable
app.jinja_env.undefined = StrictUndefined
#so that app autoreloads in debug mode (specification needed because of above)
app.jinja_env.auto_reload = True

#logic functions here:

def add_user(username, password, is_public=False):
	"""Adds new user to database, allowing them to use the website"""
	if is_public:
		user = User((username=username, password=password, 
					joined_at=datetime.now(), is_public=True))
	else: 
		user = User((username=username, password=password, 
					joined_at=datetime.now()))

	db.session.add(user)
	db.session.commit()
	user_id = user.user_id
	session["user_id"] = user_id
	flash("You have successfully registered, %s." % username)
	return user_id

#routes here:

@app.route("/")
def index():
	"""Home page route"""

	return render_template(homepage.html)

@app.route( )
def register():
	pass 

if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(port=5000)