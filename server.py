"""Server"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, session, flash)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Update, Comment, Pair, Message, connect_to_db, db

from datetime import datetime

import os

app = Flask(__name__)

#add change password functionality!

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

	user = User.query.filter(User.username == username, User.password == password).first()

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

def submit_comment(user_id, update_id, body):
	"""Creates a comment object and adds it to the database"""

	comment = Comment(update_id=update_id, user_id=user_id, comment_body=body,
		posted_at=datetime.now())

	db.session.add(comment)
	db.session.commit()

def display_comments(update_id):
	"""Displays all existing comments on an update"""

	user_comments = {}

	comments = Comment.query.filter(Comment.update_id == update_id).all()

	for comment in comments:
		user = User.query.get(comment.user_id)
		username = user.username
		time_date = datetime.strftime(comment.posted_at, "%-H:%M UTC on %B %-d, %Y")
		user_comments[comment.comment_id] = {"comment on": comment.update_id,
		"posted by": username, "posted at": time_date, 
		"body": comment.comment_body}

	return user_comments

def check_inbox(user_id):
	"""For a given user, checks what message threads they are currently in to
	then display an inbox"""

	users_in_conversations_with = []

	messages = Message.query.filter((Message.owner_id == user_id) | (Message.recipient_id == user_id)).all()
	# received_messages = Message.query.filter(Message.recipient_id == user_id).all()

	for message in messages:
		if message.owner_id not in users_in_conversations_with and message.recipient_id not in users_in_conversations_with:
			if message.owner_id == user_id:
				users_in_conversations_with.append(message.recipient_id)
			else:
				users_in_conversations_with.append(message.owner_id)

	return users_in_conversations_with

def connections(user_id):
	"""For a given user, returns list of users this user has connected with/
	authorized for communication"""

	connected_to = []

	friends = Pair.query.filter((Pair.user_1_id == user_id) | (Pair.user_2_id == user_id)).all()

	for friend in friends:
		if friend.user_1_id == user_id:
			connected_to.append(friend.user_2_id)
		if friend.user_2_id == user_id:
			connected_to.append(friend.user_1_id)

	return connected_to

def get_message_history(pair_id):
	"""For a given pair, return all messages between the two users"""

	pair = Pair.query.filter(Pair.pair_id == pair_id).first()
	messages = Message.query.filter(
		((Message.recipient_id == pair.user_1_id) | (Message.recipient_id == pair.user_2_id)), 
		((Message.owner_id == pair.user_1_id) | (Message.owner_id == pair.user_2_id)),
		Message.deleted == False).order_by(Message.sent_at).all()

	message_history = {}

	for message in messages:
		owner = User.query.get(message.owner_id)
		owner_username = owner.username
		recipient = User.query.get(message.recipient_id)
		recipient_username = recipient.username
		time_date = datetime.strftime(message.sent_at, "%-H:%M UTC on %B %-d, %Y")
		message_history[message.msg_id] = {"to": recipient_username, "from": owner_username,
		"message": message.message_body, "sent at": time_date, "read": message.read}

	return message_history

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
	"""Posts user update, adds it to the database, redirects to the homepage"""

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
	user_id = update.user_id
	user = User.query.get(user_id)
	username = user.username
	time_date = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
	user_comments = display_comments(update_id)

	return render_template("specific_update.html", username=username, text=text, 
		time_date=time_date, update_id=update_id, user_comments=user_comments)


@app.route("/add-comment/<int:update_id>", methods=["POST"])
def add_comment(update_id):
	"""Adds a specific comment to a specific update (requires user to be logged in)"""

	if "user_id" in session:
		text = request.form.get("comment")
		user_id = session["user_id"]
		submit_comment(user_id, update_id, text)
		flash("Comment submitted!")
		return redirect("/update/" + str(update_id))
	else:
		flash("You must be signed in to add a comment!")
		return redirect("/update/" + str(update_id))


@app.route("/inbox")
def show_inbox():
	"""Shows inbox contents/existing messages for users"""

	if "user_id" in session:
		user_id = session["user_id"]
		threads = check_inbox(user_id)
		return render_template("inbox.html", threads=threads)
	else:
		flash("Please sign in to view your inbox")
		return redirect("/")


@app.route("/compose-message")
def compose_message():
	"""Shows form to gather information to send a message to a fellow user"""
	
	if "user_id" in session:
		user_id = session["user_id"]
		user_ids_connected_with = connections(user_id)
		usernames_connected_with = {}
		for user_id in user_ids_connected_with:
			usernames_connected_with[user_id] = (User.query.get(user_id)).username
		return render_template("compose_message.html", usernames_connected_with=usernames_connected_with)
	else:
		flash("Please sign in to compose a message")
		return redirect("/")


@app.route("/message/<int:pair_id>")
def show_message(pair_id):
	
	pair = Pair.query.filter(Pair.pair_id == pair_id).first()
	if "user_id" in session:
		user_id = session["user_id"]
		if user_id == pair.user_1_id or user_id == pair.user_2_id:
			message_history = get_message_history(pair_id)
			return render_template("specific_message.html", message_history=message_history)
		else:
			flash("You do not have access to this page.")
			return redirect("/")
	else:
		flash("Please sign in to access messages.")
		return redirect("/login")


if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(host="0.0.0.0", port=5000)