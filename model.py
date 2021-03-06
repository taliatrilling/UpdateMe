"""Model and database functions"""

from flask_sqlalchemy import SQLAlchemy 

from datetime import datetime

from passlib.hash import bcrypt

db = SQLAlchemy()

# code help on passwords by X-Istence from http://stackoverflow.com/a/33717279

class User(db.Model):
	"""Information associated with an individual user on the site"""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	username = db.Column(db.String(20), nullable=False, unique=True)
	password = db.Column(db.String(80), nullable=False)
	joined_at = db.Column(db.DateTime, nullable=False)
	is_public = db.Column(db.Boolean, nullable=False)

	def __init__(self, username, password, joined_at, is_public, rounds=None):
		"""Passes in appropriate parameters to user instance, and creates 
		encrypted hash of password for database"""

		self.username = username
		#to make seeding db faster with fake data:
		if rounds:
			self.password = bcrypt.encrypt(password, rounds=rounds)
		else:
			self.password = bcrypt.encrypt(password)
		self.joined_at = joined_at
		self.is_public = is_public

	def validate_password(self, password):
		"""Verifies password hash, returns True or False"""

		return bcrypt.verify(password, self.password)

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return "<User user_id=%s username=%s>" % (self.user_id, self.username)


class Update(db.Model):
	"""Information associated with a specific update posted to the site"""

	__tablename__ = "updates"

	update_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	update_body = db.Column(db.String(140), nullable=False)
	posted_at = db.Column(db.DateTime, nullable=False)
	#potential other columns relating to type of update?
	
	user = db.relationship("User", backref="updates")

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<Update update_id=%d user_id=%d update_body=%s>"
				% (self.update_id, self.user_id, self.update_body))


class Comment(db.Model):
	"""Information associated with a specific comment on a specific update"""

	__tablename__ = "comments"

	comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	update_id = db.Column(db.Integer, db.ForeignKey("updates.update_id"), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	comment_body = db.Column(db.String(140), nullable=False)
	posted_at = db.Column(db.DateTime, nullable=False)

	user = db.relationship("User", backref="comments")
	update = db.relationship("Update", backref="comments")

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<Comment id=%d update_id=%d user_id=%d comment=%s>"
				% (self.comment_id, self.update_id, self.user_id, self.comment_body))


class Pair(db.Model):
	"""Permissions granted between users to see update content--only 
	relevant to users whose profile is not set to public, if a user pair 
	is not in the table, they have not yet connected"""
	#association table between users, only pairs that are connected are in the 
	#table 
	__tablename__ = "pairs" 

	pair_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False) #change to UUID version 4 potentially 
	user_1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	user_2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

	user1 = db.relationship("User", backref="pair1", foreign_keys=[user_1_id])
	user2 = db.relationship("User", backref="pair2", foreign_keys=[user_2_id])

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<Pair_id=%d user_1_id=%d user_2_id=%d>"
				% (self.pair_id, self.user_1_id, self.user_2_id))

class Message(db.Model):
	"""Messages between a pair of users"""

	__tablename__ = "messages"

	msg_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	recipient_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	sent_at = db.Column(db.DateTime, nullable=False)
	message_body = db.Column(db.String(140), nullable=False)
	read = db.Column(db.Boolean, default=False)
	deleted = db.Column(db.Boolean, default=False)

	owner = db.relationship("User", backref="user_owner", foreign_keys=[owner_id])
	recipient = db.relationship("User", backref="user_recipient", foreign_keys=[recipient_id])

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<msg_id=%d owner_id=%d recipient_id=%d message_body=%s>"
				% (self.msg_id, self.owner_id, self.recipient_id, self.message_body))

class Request(db.Model):
	"""Requests from one user to another to connect"""

	__tablename__ = "requests"

	request_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	requester_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	requestee_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

	requester = db.relationship("User", backref="user_requester", foreign_keys=[requester_id])
	requestee = db.relationship("User", backref="user_requestee", foreign_keys=[requestee_id])

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<request_id=%d requester_id=%d requestee_id=%d>"
				% (self.request_id, self.requester_id, self.requestee_id))

class Notification(db.Model):
	"""Notifications to display to a user, after clicked on, 'viewed' column is updated"""

	__tablename__ = "notifications"

	notification_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	notification_type = db.Column(db.String(10), nullable=False) # "msg", "req", "apr"
	added_at = db.Column(db.DateTime, nullable=False)
	viewed = db.Column(db.Boolean, default=False, nullable=False)

	user = db.relationship("User", backref="notifications")

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return ("<notification_id=%d user_id=%d notification_type=%s>" 
			% (self.notification_id, self.user_id, self.notification_type))

def fake_test_data():
	"""Creates sample data for unittests to use"""

	user1 = User(username="shepard", password="password123", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=True)
	user2 = User(username="garrus", password="pass123", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=False)
	user3 = User(username="wrex", password="pword", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=True)
	user4 = User(username="liara", password="passpass", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=False)
	user5 = User(username="saren", password="evildude", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=False)
	user6 = User(username="jenkins", password="npclyfe", joined_at=datetime(2016, 11, 11, 0, 0, 31, 645845), is_public=True)

	update1 = Update(user_id=2, update_body="just in the middle of some calibrations", posted_at=datetime(2016, 11, 11, 0, 2, 16, 227091))
	update2 = Update(user_id=1, update_body="anyone want to open this bottle of serrice ice I got for Chakwas with me?", posted_at=datetime(2016, 11, 11, 0, 2, 16, 227091))
	update3 = Update(user_id=4, update_body="please stop calling me the shadow broker, I'm totally not her--I mean, them...", posted_at=datetime(2016, 11, 11, 0, 2, 16, 227091))
	update4 = Update(user_id=5, update_body="I'm so going to betray Nihlus ;)", posted_at=datetime(2016, 11, 11, 0, 2, 16, 227091))
	update5 = Update(user_id=6, update_body="Yay first day at work I'm totally not going to die!", posted_at=datetime(2016, 11, 11, 0, 2, 16, 227091))

	comment1 = Comment(update_id=2, user_id=3, comment_body="Shepard.", posted_at=datetime(2016, 11, 11, 0, 2, 45, 185511))
	comment2 = Comment(update_id=2, user_id=1, comment_body="Wrex.", posted_at=datetime(2016, 11, 11, 0, 2, 45, 185511))
	comment3 = Comment(update_id=2, user_id=2, comment_body="you guys are weird...", posted_at=datetime(2016, 11, 11, 0, 2, 45, 185511))

	message1 = Message(owner_id=1, recipient_id=2, sent_at=datetime(2016, 11, 11, 0, 13, 47, 182798), message_body="up for another contest on the citadel later?")
	message2 = Message(owner_id=2, recipient_id=1, sent_at=datetime(2016, 11, 11, 0, 15, 0, 59559), message_body="hell yes")

	connection1 = Pair(user_1_id=1, user_2_id=2)
	connection2 = Pair(user_1_id=3, user_2_id=1)
	connection3 = Pair(user_1_id=4, user_2_id=1)
	connection4 = Pair(user_1_id=2, user_2_id=3)

	request1 = Request(requester_id=4, requestee_id=2)
	request2 = Request(requester_id=6, requestee_id=1)

	notification1 = Notification(user_id=1, notification_type="msg", added_at=datetime(2016, 11, 11, 0, 15, 0, 59559))
	notification2 = Notification(user_id=1, notification_type="req", added_at=datetime(2016, 11, 11, 0, 15, 0, 59559))
	notification3 = Notification(user_id=2, notification_type="req", added_at=datetime(2016, 11, 11, 0, 15, 0, 59559))

	db.session.add_all([user1, user2, user3, user4, user5, user6, update1, update2, 
		update3, update4, update5, comment1, comment2, comment3, message1, message2, 
		connection1, connection2, connection3, connection4, request1, request2,
		notification1, notification2, notification3])
	db.session.commit()


def connect_to_db(app, uri="postgresql:///twitterclone"):
	"""Connects the PostgreSQL database to the Flask app"""

	app.config['SQLALCHEMY_DATABASE_URI'] = uri
	db.app = app
	db.init_app(app)

if __name__ == '__main__':
	from server import app 
	connect_to_db(app)
	db.create_all()




