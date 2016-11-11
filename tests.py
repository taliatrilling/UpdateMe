from server import app
import server as s 
from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db, fake_test_data
import unittest
from flask_sqlalchemy import SQLAlchemy 
from flask import (Flask, render_template, redirect, request, session, flash, jsonify)


class LogicTestCases(unittest.TestCase):
	"""Tests logic/helper functions used by the server"""

	def setUp(self):
		connect_to_db(app, "postgresql:///twitterclonetest")
		db.create_all()
		fake_test_data()

	def test_add_user_public(self):
		self.assertEqual(s.add_user("chakwas", "password", 1), 
			(User.query.filter(User.username == "chakwas").first()).user_id)
		self.assertTrue((User.query.filter(User.username == "chakwas").first()).is_public)

	def test_add_user_private(self):
		self.assertEqual(s.add_user("tali", "password", 2), 
			(User.query.filter(User.username == "tali").first()).user_id)
		self.assertFalse((User.query.filter(User.username == "tali").first()).is_public)

	def test_check_valid_user_credentials(self):
		self.assertEqual(s.check_user_credentials("shepard", "password123"),
			(User.query.filter(User.username == "shepard").first()).user_id)

	def test_check_fake_user_credentials(self):
		self.assertFalse(s.check_user_credentials("shepard", "lolno"))

	def test_submit_update(self):
		user_id = (User.query.filter(User.username == "shepard").first()).user_id
		self.assertEqual(s.submit_update(user_id, "I love the Normandy"), 
			(Update.query.filter(Update.update_body == "I love the Normandy").first()).update_id)

	def test_submit_comment(self):
		user_id = (User.query.filter(User.username == "garrus").first()).user_id
		self.assertEqual(s.submit_comment(user_id, 3, "uh whatever you say..."), 
			(Comment.query.filter(Comment.comment_body == "uh whatever you say...").first()).comment_id)

	def test_display_comments(self):
		comments = {1 :{"comment on": 2, "posted by": "wrex", "posted at": "0:02 UTC on November 11, 2016", "body": "Shepard."}, 
		2: {"comment on": 2, "posted by": "shepard", "posted at": "0:02 UTC on November 11, 2016", "body": "Wrex."},
		3: {"comment on": 2, "posted by": "garrus", "posted at": "0:02 UTC on November 11, 2016", "body": "you guys are weird..."}}
		self.assertEqual(s.display_comments(2),comments)

	def test_check_inbox(self):
		self.assertEqual(s.check_inbox(2), [1])

	def test_check_connections(self):
		self.assertEqual(s.connections(1), [2, 3, 4])

	def test_get_message_history(self):
		messages = {1: {"to": u"garrus", "from": u"shepard", "message": u"up for another contest on the citadel later?", 
		"sent at": "0:13 UTC on November 11, 2016", "read": False}, 2: {"to": u"shepard", "from": u"garrus", 
		"message": u"hell yes", 
		"sent at": "0:15 UTC on November 11, 2016", "read": False}}
		self.assertEqual(s.get_message_history(1), messages)


	def tearDown(self):
		db.session.close()
		db.drop_all()


class RouteTestCases(unittest.TestCase):
	pass

if __name__ == '__main__':
	unittest.main()