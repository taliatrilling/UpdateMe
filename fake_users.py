from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import factory
from faker import Factory as FakerFactory
from datetime import datetime
from server import app

#see docs for Faker at https://faker.readthedocs.io/en/latest/
#see docs for factory_boy at https://factoryboy.readthedocs.io/en/latest/

faker = FakerFactory.create()

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
	"""Creates fake users"""

	class Meta:
		model = User
		sqlalchemy_session = db.session

	username = faker.user_name()
	password = faker.word()
	joined_at = faker.date_time_this_year(before_now=True, after_now=False, tzinfo=None)
	is_public = faker.boolean()


# class UserUpdate(factory.alchemy.SQLAlchemyModelFactory):
# 	"""Creates fake updates from fake users"""



#to use:
#ipython -i factory_set_up.py 
#connect_to_db(app)
#UserFactory.create()
# do as many times as needed
#db.session.commit()