import server
from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import unittest

class LogicTestCases(unittest.TestCase):
	"""Tests logic/helper functions used by the server"""

	def setUp(self):
		pass

	def test_add_user_public(self):
		pass
		add_user("taliamax", password, is_public)

	def test_add_user_private(self):
		pass

	def test_check_user_credentials(self):
		pass

	def tearDown(self):
		pass




class RouteTestCases(unittest.TestCase):
	pass

if __name__ == '__main__':
	unittest.main()