from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import factory
from faker import Factory as FakerFactory
from datetime import datetime
from server import app
import random

#see docs for Faker at https://faker.readthedocs.io/en/latest/
#see docs for factory_boy at https://factoryboy.readthedocs.io/en/latest/

faker = FakerFactory.create()


def add_users():
	"""Adds fake users to db, in theory should add 500 but usually fails before it can reach 500 
	because the system will try to use the same fake username"""

	for i in range(500):
		user = User(username=faker.user_name(), password=faker.word(), 
			joined_at=faker.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
			is_public=faker.boolean())
		db.session.add(user)
		db.session.commit()

def add_updates():
	"""Adds fake updates to the system"""

	current_users = db.session.query(User.user_id).all()
	for i in range(500):
		update = Update(user_id=random.choice(current_users), update_body=faker.text(max_nb_chars=140), 
			posted_at=datetime.now())
		db.session.add(update)
		db.session.commit()


