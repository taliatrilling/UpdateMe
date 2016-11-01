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

	user = User.query.filter(username == username, password == password).first()

	if user:
		user_id = user.user_id
		session["user_id"] = user_id
		flash("You were successfully signed in, %s" % username)
		return True
	else:
		flash("Your username or password was invalid, please try again.")
		return False

def submit_update(user_id, body):
	"""Creates an update object with the text body and user_id passed in"""

	update = Update(user_id=user_id, update_body=body, posted_at=datetime.now())

	db.session.add(update)
	db.session.commit()

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

#change to 0 and 1 
	if is_public == "1":
		public = 1
		add_user(username, password, 1)
	if is_public == "2":
		public = 2
		add_user(username, password, 2)

	return redirect("/")


@app.route("/login")
def login():
	"""Displays the login form for an existing user"""

	return render_template("login.html")


@app.route("/login-success", methods=["POST"])
def login_success():
	"""Checks if the user's password is valid for their username, if so,
	logs the user in via a session cookie and redirects home, if not, flashes 
	an error message and redirects back to the login page"""
	
	username = request.form.get("username")
	password = request.form.get("password")	

	success = check_user_credentials(username, password)

	if success:
		return redirect("/")
	if not success:
		return redirect("/login")


@app.route("/logout")
def logout():
	"""Logs out user by deleting the session cookie, flashes success message 
	and redirects home"""

	del session["user_id"]
	flash("You have successfully been logged out")
	return redirect("/")


@app.route("/compose-update")
def compose_update():
	"""If user is logged in via session cookie, displays form to submit update,
	otherwise redirects home"""

	if "user_id" in session:
		return render_template("update.html")
	else: 
		flash("Please sign in to post an update")
		return redirect("/")


@app.route("/update-posted", methods=["POST"])
def post_update():

	user_id = session["user_id"]
	body = request.form.get("textbody")

	submit_update(user_id, body)
	flash("Your update has been successfully posted!")
	return redirect("/")

@app.route("/update/<int:update_id>")
def show_specific_update(update_id):
	"""Shows a specific update as associated with its update id"""

	update = Update.query.get(update_id)
	text = update.update_body

	return render_template("specific_update.html", update_id=update_id, text=text)


if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(host="0.0.0.0", port=5000)