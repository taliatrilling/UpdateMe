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

#logic functions here:

def add_user(username, password, is_public):
	"""Adds new user to database, allowing them to use the website"""
	if is_public == 1:
		user = User(username=username, password=password, 
					joined_at=datetime.now(), is_public=True)
	if is_public == 2:
		user = User(username=username, password=password, 
					joined_at=datetime.now(), is_public=False)

	db.session.add(user)
	db.session.commit()
	user_id = user.user_id
	session["user_id"] = user_id
	flash("You have successfully registered, %s." % username)
	return user_id

def check_user_credentials(username, password):
	"""Checks the validity of a username and password"""

	if not User.query.filter(username == username, password == password).first():
		flash("Your username or password was invalid, please try again.")
	else:
		user = User.query.filter(username == username, password == password).first()
		user_id = user.user_id
		session["user_id"] = user_id
		flash("You were successfully signed in, %s" % username)

#routes here:

@app.route("/")
def index():
	"""Home page route"""

	return render_template("homepage.html")

@app.route("/register")
def register():
	"""Displays registration form"""
	
	return render_template("register.html")

@app.route("/register-success", methods=["POST"])
def register_success():
	"""Takes information provided in the registration form, adds the user to 
	the database, and then redirects to the homepage with a flash success 
	message"""

	username = request.form.get("username")
	password = request.form.get("password")
	is_public = request.form.get("is_public")

	if is_public == "1":
		public = 1
		add_user(username, password, 1)
	if is_public == "2":
		public = 2
		add_user(username, password, 2)

	return redirect("/")


if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(host="0.0.0.0", port=5000)