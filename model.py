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


# class Permission(db.Model):
# 	"""Permissions granted between users to see update content--only 
# 	relevant to users whose profile is not set to public"""

# 	__tablename__ = "permission" 


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




