from server import app
import server as s 
from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db
import unittest
from flask_sqlalchemy import SQLAlchemy 
from flask import (Flask, render_template, redirect, request, session, flash, jsonify)


class LogicTestCases(unittest.TestCase):
	"""Tests logic/helper functions used by the server"""

	def setUp(self):
		app.debug = True
		app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///twitterclonetest"
		db.app = app
		db.init_app(app)

	def test_add_user_public(self):
		self.assertEqual(s.add_user("testuser", "password", 1), 
			(User.query.filter(User.username == "testuser").first()).user_id)
		self.assertTrue((User.query.filter(User.username == "testuser").first()).is_public)

	def test_add_user_private(self):
		self.assertEqual(s.add_user("testuserprivate", "password", 2), 
			(User.query.filter(User.username == "testuserprivate").first()).user_id)
		self.assertFalse((User.query.filter(User.username == "testuserprivate").first()).is_public)

	def test_check_valid_user_credentials(self):
		self.assertEqual(s.check_user_credentials("testuser", "password"),
			User.query.filter(User.username == "testuser").first()).user_id)

	def test_check_fake_user_credentials(self):
		self.assertFalse(s.check_user_credentials("totallynotauser", "password"))

	def tearDown(self):
		#something to drop the db 
		pass


class RouteTestCases(unittest.TestCase):
	pass

if __name__ == '__main__':
	unittest.main()