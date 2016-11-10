from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import factory
from faker import Factory as FakerFactory
from datetime import datetime
from server import app, pair_lookup
import random

#see docs for Faker at https://faker.readthedocs.io/en/latest/
#see docs for factory_boy at https://factoryboy.readthedocs.io/en/latest/

faker = FakerFactory.create()


def add_users():
	"""Adds fake users to db, in theory should add 500 but usually fails before it can reach 500 
	because the system will try to use the same fake username"""

	for i in range(5000):
		user = User(username=(faker.first_name() + faker.pystr(min_chars=3, max_chars=7)), 
			password=faker.password(length=10, special_chars=False, digits=True, upper_case=True, lower_case=True), 
			joined_at=faker.date_time_this_year(before_now=True, after_now=False, tzinfo=None),
			is_public=faker.boolean(), rounds=4)
		db.session.add(user)
		db.session.commit()

def add_updates():
	"""Adds fake updates to the system"""

	current_users = db.session.query(User.user_id).all()
	for i in range(5000):
		update = Update(user_id=random.choice(current_users), update_body=faker.text(max_nb_chars=140), 
			posted_at=datetime.now())
		db.session.add(update)
		db.session.commit()

def add_connections():
	"""Adds fake user connections to the system"""

	current_users = db.session.query(User.user_id).all()
	for i in range(2000):
		user1 = random.choice(current_users)
		user2 = random.choice(current_users)
		if user1 != user2 and not pair_lookup(user1, user2):
			pair = Pair(user_1_id=user1, user_2_id=user2)
			db.session.add(pair)
			db.session.commit()



