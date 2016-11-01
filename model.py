"""Model and database functions"""

from flask_sqlalchemy import SQLAlchemy 

from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
	"""Information associated with an individual user on the site"""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	password = db.Column(db.String(20), nullable=False)
	joined_at = db.Column(db.DateTime, nullable=False)
	is_public = db.Column(db.Boolean, nullable=False)
	#profile_picture
	#user_preferences ? 

	def __repr__(self):
		"""Provides useful representation of an instance when printed"""

		return "<User user_id=%d username=%s>" % (self.user_id, self.username)


class Update(db.Model):
	"""Information associated with a specific update posted to the site"""

	__tablename__ = "updates"

	update_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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

	comment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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

	pair_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_1_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
	user_2_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

	user1 = db.relationship("User", backref="pair1", foreign_keys=[user_1_id])
	user2 = db.relationship("User", backref="pair2", foreign_keys=[user_2_id])

def connect_to_db(app):
	"""Connects the PostgreSQL database to the Flask app, defaults to use the 
	primary DB, but allows for a different argument to be passed in for 
	testing purposes"""

	#uri="postgresql:///twitterclone"
	# app.config["SQLALCHEMY_DATEBASE_URI"] = uri 
	app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///twitterclone"
	db.app = app
	db.init_app(app)

if __name__ == '__main__':
	from server import app 
	connect_to_db(app)
	db.create_all()




