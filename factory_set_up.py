from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import factory
from datetime import datetime
from server import app



class UserFactoryPublic(factory.alchemy.SQLAlchemyModelFactory):
	""" """
	class Meta:
		model = User
		sqlalchemy_session = db.session

	username = factory.Sequence(lambda n: "username%d" % n)
	password = "password123"
	joined_at = factory.LazyFunction(datetime.now)
	is_public = True

class UserFactoryPrivate(factory.alchemy.SQLAlchemyModelFactory):
	""" """
	class Meta:
		model = User
		sqlalchemy_session = db.session

	username = factory.Sequence(lambda n: "username%d" % n)
	password = "password123"
	joined_at = factory.LazyFunction(datetime.now)
	is_public = False

#to use:
#ipython -i factory_set_up.py 
#connect_to_db(app)
#UserFactoryPublic.create() [or UserFactoryPrivate.create()]
# do as many times as needed
#db.session.commit()
