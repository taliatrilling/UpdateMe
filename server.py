"""Server"""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, session, flash, jsonify)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db

from datetime import datetime

from passlib.hash import bcrypt

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
		username = username.lower()
		user = User(username=username, password=password, 
					joined_at=datetime.now(), is_public=True)
	if is_public == 2:
		username = username.lower()
		user = User(username=username, password=password, 
					joined_at=datetime.now(), is_public=False)

	db.session.add(user)
	db.session.commit()
	user_id = user.user_id
	username = user.username
	return user_id

def check_user_credentials(username, password):
	"""Checks the validity of a username and password"""

	user = User.query.filter(User.username == username).first()
	password_hashed = User.validate_password(user, password)

	if password_hashed:
		user_id = user.user_id
		username = user.username
		return user_id
	else:
		return False

def submit_update(user_id, body):
	"""Creates an update object with the text body and user_id passed in"""

	update = Update(user_id=user_id, update_body=body, posted_at=datetime.now())

	db.session.add(update)
	db.session.commit()

	return update.update_id

def submit_comment(user_id, update_id, body):
	"""Creates a comment object and adds it to the database"""

	comment = Comment(update_id=update_id, user_id=user_id, comment_body=body,
		posted_at=datetime.now())

	db.session.add(comment)
	db.session.commit()

	return comment.comment_id

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
	"""For a given pair, return the 10 most recent messages between the two users"""

	pair = Pair.query.filter(Pair.pair_id == pair_id).first()
	messages = Message.query.filter(
		((Message.recipient_id == pair.user_1_id) | (Message.recipient_id == pair.user_2_id)), 
		((Message.owner_id == pair.user_1_id) | (Message.owner_id == pair.user_2_id)),
		Message.deleted == False).order_by(Message.sent_at).limit(10).all()

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

def which_pair_by_active_user(user_id, pair_id):
	"""When logged in as a user, for pairs that the user is in, when given a 
	certain pair_id, returns the user_id of the other user in the pair"""

	pair = Pair.query.filter(Pair.pair_id == pair_id).first()
	
	if user_id != pair.user_1_id and user_id != pair.user_2_id:
		return False
	if user_id == pair.user_1_id:
		other_user = User.query.get(pair.user_2_id)
		return other_user.user_id
	if user_id == pair.user_2_id:
		other_user = User.query.get(pair.user_1_id)
		return other_user.user_id

def submit_message_to_db(user_id, recipient_id, message_body):
	"""Adds a message instance to the db"""

	message = Message(owner_id=user_id, recipient_id=recipient_id,
		sent_at=datetime.now(), message_body=message_body)
	db.session.add(message)
	db.session.commit()
	return message.msg_id

def pair_lookup(user_1_id, user_2_id):
	"""For two users, finds the pair_id for the connection (if exists)"""

	pair = Pair.query.filter((Pair.user_1_id == user_1_id) | (Pair.user_1_id == user_2_id),
		(Pair.user_2_id == user_1_id) | (Pair.user_2_id == user_2_id)).first()

	if pair: 
		return pair.pair_id

def show_feed_all(offset_num):
	"""Show 20 most recent public updates"""

	public_users = db.session.query(User.user_id).filter(User.is_public == True).all()
	updates = Update.query.filter(Update.user_id.in_(public_users)).order_by(Update.posted_at.desc()).limit(20).offset(offset_num).all()
	all_updates = []
	for update in updates:
		username = (User.query.get(update.user_id)).username
		posted = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
		user_id = (User.query.get(update.user_id)).user_id
		all_updates.append([username, update.update_body, posted, user_id, update.update_id])
	return all_updates

def all_connections_for_current_user(current_user_id):
	"""Used to show feed connections, for the current user returns a list of user_ids connected with"""

	pairs_in = Pair.query.filter((Pair.user_1_id == current_user_id) | (Pair.user_2_id == current_user_id)).all()
	pairs_with = []
	for pair in pairs_in:
		if pair.user_1_id == current_user_id:
			pairs_with.append(pair.user_2_id)
		if pair.user_2_id == current_user_id:
			pairs_with.append(pair.user_1_id)
	return pairs_with

		
def show_feed_connections(offset_num, current_user_id):
	"""Show 20 most recent updates created by connections"""
	
	pairs_with = all_connections_for_current_user(current_user_id)
	updates = Update.query.filter(Update.user_id.in_(pairs_with)).order_by(Update.posted_at.desc()).limit(20).offset(offset_num).all()
	all_updates = []
	for update in updates:
		username = (User.query.get(update.user_id)).username
		posted = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
		user_id = (User.query.get(update.user_id)).user_id
		all_updates.append([username, update.update_body, posted, user_id, update.update_id])
	return all_updates

def all_updates_for_specific_user(user_id):
	"""Returns a list of update objects represent the updates a user has posted"""
	
	updates = Update.query.filter(Update.user_id == user_id).order_by(Update.posted_at).all()
	return updates

def add_connection_request(current_user_id, other_user_id):
	"""Adds a connection request to the db"""

	new_request = Request(requester_id=current_user_id, requestee_id=other_user_id)
	db.session.add(new_request)
	db.session.commit()
	return new_request.request_id

def add_pair_to_db(current_user_id, user_connecting_with_id):
	"""Adds a pair to the database, should only be called after a connection has been
	requested by one user and accepted by the other"""

	pair = Pair(user_1_id=user_connecting_with_id, user_2_id=current_user_id)
	db.session.add(pair)
	db.session.commit()
	other_user_username = (User.query.filter(User.user_id == user_connecting_with_id).first()).username
	Request.query.filter(Request.requester_id == user_connecting_with_id, Request.requestee_id == current_user_id).delete()
	db.session.commit()
	return pair.pair_id

def get_connection_requests(current_user_id):
	"""Fetches from the database any outstanding connection requests for the current user"""

	current_requests = Request.query.filter(Request.requestee_id == current_user_id).all()
	return current_requests

def usernames_behind_connection_requests(current_requests):
	"""For current requests, returns a list of usernames representing who requested connection"""

	usernames = []
	for request in current_requests:
		username = (User.query.get(request.requester_id)).username
		usernames.append(username)

	return usernames

def change_password(current_user_id, new_password):
	"""Changes the password of the current user"""

	user = User.query.get(current_user_id)
	user.password = bcrypt.encrypt(new_password)
	db.session.commit()

	if bcrypt.verify(new_password, user.password):
		return True
	else:
		return False

@app.route("/")
def index():
	"""Home page route"""

	return render_template("homepage.html")


@app.route("/register")
def register():
	"""Displays registration form"""

	if "user_id" in session:
		flash("You are already logged into an account, please log out if you would like to register another account.")
		return redirect("/")
	else:
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
		user_id = add_user(username, password, 1)
	if is_public == "2":
		public = 2
		user_id = add_user(username, password, 2)

	session["user_id"] = user_id
	session["username"] = username
	flash("You have successfully registered, %s." % username)
	return redirect("/")


@app.route("/login")
def login():
	"""Displays the login form for an existing user"""

	if "user_id" in session:
		flash("You are already logged in.")
		return redirect("/")
	else:
		return render_template("login.html")


@app.route("/login-success", methods=["POST"])
def login_success():
	"""Checks if the user's password is valid for their username, if so,
	logs the user in via a session cookie and redirects home, if not, flashes 
	an error message and redirects back to the login page"""
	
	username = request.form.get("username")
	password = request.form.get("password")	

	user_id = check_user_credentials(username, password)

	if user_id:
		session["user_id"] = user_id
		session["username"] = username
		flash("You were successfully signed in, %s" % username)
		return redirect("/")
	if not user_id:
		flash("Your username or password was invalid, please try again.")
		return redirect("/login")


@app.route("/logout")
def logout():
	"""Logs out user by deleting the session cookie, flashes success message 
	and redirects home"""

	del session["user_id"]
	del session["username"]
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

	if "user_id" in session:
		current_user_id = session["user_id"]
		update = Update.query.get(update_id)
		text = update.update_body
		user_id = update.user_id
		user = User.query.get(user_id)
		if user.is_public:
			username = user.username
			time_date = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
			user_comments = display_comments(update_id)

			return render_template("specific_update.html", username=username, text=text, 
				time_date=time_date, update_id=update_id, user_comments=user_comments, user_id=user_id)
		else:
			if pair_lookup(user_id, current_user_id):
				username = user.username
				time_date = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
				user_comments = display_comments(update_id)

				return render_template("specific_update.html", username=username, text=text, 
					time_date=time_date, update_id=update_id, user_comments=user_comments, user_id=user_id)
			else:
				flash("You do not have access to this user's updates.")
				return redirect("/")
	else:
		update = Update.query.get(update_id)
		text = update.update_body
		user_id = update.user_id
		user = User.query.get(user_id)
		if user.is_public:
			username = user.username
			time_date = datetime.strftime(update.posted_at, "%-H:%M UTC on %B %-d, %Y")
			user_comments = display_comments(update_id)

			return render_template("specific_update.html", username=username, text=text, 
				time_date=time_date, update_id=update_id, user_comments=user_comments, user_id=user_id)
		else:
			flash("You do not have access to this user's updates.")
			return redirect("/")

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
		users_talking_to = {}
		for thread in threads:
			user = User.query.filter(User.user_id == thread).first()
			username = user.username
			connection_id = pair_lookup(user_id, thread)
			users_talking_to[username] = connection_id
		return render_template("inbox.html", users_talking_to=users_talking_to)
	else:
		flash("Please sign in to view your inbox")
		return redirect("/")


@app.route("/message/<int:pair_id>")
def show_message(pair_id):
	"""For a pair, displays the messages between the two users (if any)"""
	
	pair = Pair.query.filter(Pair.pair_id == pair_id).first()
	if "user_id" in session:
		user_id = session["user_id"]
		if which_pair_by_active_user(user_id, pair_id):
			other_user_id = which_pair_by_active_user(user_id, pair_id)
			other_user = (User.query.get(other_user_id)).username
			if user_id == pair.user_1_id or user_id == pair.user_2_id:
				message_history = get_message_history(pair_id)
				return render_template("specific_message.html", message_history=message_history,
					other_user=other_user, other_user_id=other_user_id)
			else:
				flash("You do not have access to this page.")
				return redirect("/")
		else:
			flash("You do not have access to this page.")
			return redirect("/")
	else:
		flash("Please sign in to access messages.")
		return redirect("/login")


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


@app.route("/submit-message", methods=["POST"])
def submit_message():
	"""Adds user's message to a connection to the db and redirects to that
	conversation thread"""
	
	user_id = session["user_id"]
	message_body = request.form.get("message")
	recipient = request.form.get("chosen-recipient")
	recipient_id = int(recipient)

	submit_message_to_db(user_id, recipient_id, message_body)

	pair = pair_lookup(user_id, recipient_id)

	flash("Your message has been sent!")
	return redirect("/message/" + str(pair))


@app.route("/submit-reply-message", methods=["POST"])
def submit_reply_message():
	"""Adds user's message to a connection to the db and shows success message
	(in contrast to submit_message function, user does not need to specify who
	the message is to, as it is a reply to an existing conversation)"""
	
	user_id = session["user_id"]
	message_body = request.form.get("message")
	other_user_id = request.form.get("recipient")

	submit_message_to_db(user_id, other_user_id, message_body)

	pair = pair_lookup(user_id, other_user_id)

	flash("Your message has been sent!")
	return redirect("/message/" + str(pair))


@app.route("/check-username")
def check_username():
	"""Route for username validation--checks if a given username is already in the system"""
	username = request.args.get("username")
	if User.query.filter(User.username == username.lower()).first():
		return "exists"
	elif User.query.filter(User.username == username).first():
		return "exists"
	else:
		return "available"


@app.route("/feed-all-json")
def see_all_feed():
	"""Calls the function that returns the json for 20 most recent public updates"""
	
	offset = request.args.get("offset")
	feed_json = show_feed_all(offset)
	return jsonify({"results": feed_json})


@app.route("/search-results")
def search_db():
	"""Takes in the user's input to conduct a search of the entire database,
	including users and updates (updates only if content is public)"""

	user_input = request.args.get("search")

	matching_users = User.query.filter(User.username.like("%"+user_input+"%")).all()
	matching_updates = Update.query.filter(Update.update_body.like("%"+user_input+"%")).all()


	return render_template("search_results.html", matching_users=matching_users,
		matching_updates=matching_updates)

@app.route("/profile/<int:user_id>")
def show_profile(user_id):
	"""For a given user, shows their profile if the account is public, or if the current user is connected to
	the user in question. If they are not connected, displays an option to request to connect"""

	
	user_of_interest = User.query.filter(User.user_id == user_id).first()

	if "user_id" in session:
		current_user_id = session["user_id"]
		if user_of_interest.user_id == current_user_id:
			updates = all_updates_for_specific_user(user_id)
			return render_template("user_profile.html", updates=updates)
		elif user_of_interest.is_public: 
			if pair_lookup(user_of_interest.user_id, current_user_id):
				updates = all_updates_for_specific_user(user_id)
				return render_template("public_profile_connected.html", user_of_interest=user_of_interest, updates=updates)
			else:
				updates = all_updates_for_specific_user(user_id)
				return render_template("public_profile.html", user_of_interest=user_of_interest, updates=updates)
		else:
			if pair_lookup(user_of_interest.user_id, current_user_id):
				updates = all_updates_for_specific_user(user_of_interest.user_id)
				return render_template("shared_private_profile.html", user_of_interest=user_of_interest, updates=updates)
			else:
				return render_template("profile_private.html", user_of_interest=user_of_interest)
	else:
		flash("Please log in to view a user's profile")
		return redirect ("/")


@app.route("/feed-connects-json")
def see_connections_feed():
	"""Calls and returns result of logic function querying 20 most recent 
	updates from connections only"""

	user_id = session["user_id"]
	offset = request.args.get("connectionoffset")
	feed_json = show_feed_connections(offset, user_id)
	return jsonify({"results": feed_json})


@app.route("/request-connection/<int:other_user_id>", methods=["POST"])
def request_connection(other_user_id):
	"""Request a connection with a specific user"""
	
	current_user_id = session["user_id"]
	if Request.query.filter(Request.requester_id == current_user_id, Request.requestee_id == other_user_id).first():
		flash("You have already requested a connection with this user")
		return redirect("/profile/" + str(other_user_id))

	add_connection_request(current_user_id, other_user_id)
	flash("Your request has been sent")
	return redirect("/profile/" + str(other_user_id))


@app.route("/review-connection-requests")
def review_requests():
	"""Displays information about requested connections involving the current user"""

	current_user_id = session["user_id"]
	current_requests = get_connection_requests(current_user_id)
	usernames = usernames_behind_connection_requests(current_requests)

	return render_template("connection_requests.html", current_requests=current_requests, usernames=usernames)


@app.route("/approve-connection/<int:request_id>")
def approve_request(request_id):
	"""Takes in the information for a request a user has approved and calls the function to add the 
	pair to the pairs db"""

	current_user_id = session["user_id"]
	user_connecting_with_id = (Request.query.filter(Request.request_id == request_id).first()).requester_id
	add_pair_to_db(current_user_id, user_connecting_with_id)
	flash("You have successfully connected with" + other_user_username)
	return redirect("/review-connection-requests")


@app.route("/preferences/change-password-success", methods=["POST"])
def change_password_success():
	"""Calls function to change user password if correctly validated, redirects to profile and displays success message"""
	
	user_id = session["user_id"]
	username = session["username"]
	current_password = request.form.get("current_password")
	new_password = request.form.get("new_password")
	validation_success = check_user_credentials(username, current_password)

	if validation_success:
		change_password(user_id, new_password)
		flash("Your password has been successfully changed.")
		return redirect("/profile/" + str(user_id))
	else:
		flash("Your current password was entered incorrectly, please try again.")
		return redirect("/profile/" + str(user_id))



if __name__ == '__main__':
	app.debug = True
	connect_to_db(app)
	DebugToolbarExtension(app)
	app.run(host="0.0.0.0", port=5000)