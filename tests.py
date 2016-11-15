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

	def test_which_pair_by_active_user(self):
		self.assertEqual(s.which_pair_by_active_user(1, 1), 2) 

	def test_submit_message_to_db(self):
		self.assertEqual(s.submit_message_to_db(3, 1, "Shepard."), 3)
		self.assertTrue(Message.query.filter(Message.msg_id == 3, Message.message_body == "Shepard.").first())

	def test_pair_lookup_exists(self):
		self.assertEqual(s.pair_lookup(1, 2), 1)

	def test_pair_lookup_does_not_exist(self):
		self.assertIsNone(s.pair_lookup(4, 2))

	def test_show_feed_all(self):
		all_updates = [[u"shepard", u"anyone want to open this bottle of serrice ice I got for Chakwas with me?", "0:02 UTC on November 11, 2016", 1, 2]]
		self.assertEqual(s.show_feed_all(0), all_updates)

	def test_all_connections_for_current_user(self):
		self.assertEqual(s.all_connections_for_current_user(1), [2,3,4])

	def test_show_feed_connections(self):
		all_updates = [[u"garrus", u"just in the middle of some calibrations", "0:02 UTC on November 11, 2016", 2, 1],
		[u"liara", u"please stop calling me the shadow broker, I'm totally not her--I mean, them...", "0:02 UTC on November 11, 2016", 4, 3]]
		self.assertEqual(s.show_feed_connections(0, 1), all_updates)

	def test_all_updates_for_specific_user(self):
		updates = Update.query.filter(Update.user_id == 1).all()
		self.assertEqual(s.all_updates_for_specific_user(1), updates)

	def test_add_connection_request(self):
		self.assertEqual(s.add_connection_request(3, 4), 2)
		self.assertIsNotNone(Request.query.filter(Request.request_id == 2).first())

	def test_add_pair_to_db(self):
		self.assertEqual(s.add_pair_to_db(3, 4), 5)
		self.assertIsNotNone(Pair.query.filter(Pair.pair_id == 5).first())

	def test_get_connection_requests(self):
		requests = Request.query.filter(Request.requestee_id == 2).all()
		self.assertEqual(s.get_connection_requests(2), requests)

	def test_get_connection_requests_when_none(self):
		self.assertEqual(s.get_connection_requests(1), [])

	def test_usernames_behind_connection_requests(self):
		requests = Request.query.filter(Request.requestee_id == 2).all()
		self.assertEqual(s.usernames_behind_connection_requests(requests), ["liara"])

	def test_change_password(self):
		pass

	def test_change_public_or_private(self):
		pass

	def tearDown(self):
		db.session.close()
		db.drop_all()


class RouteTestCasesSession(unittest.TestCase):
	"""Tests flask route functions in server that use session keys/rely on session keys to know to redirect"""

	def setUp(self):
		connect_to_db(app, "postgresql:///twitterclonetest")
		db.create_all()
		fake_test_data()
		self.client = s.app.test_client()
		s.app.config['TESTING'] = True
		s.app.config["SECRET_KEY"] = "masseffectrulez"
		with self.client as c:
			with c.session_transaction() as sess:
				sess["user_id"] = 1
				sess["username"] = "shepard"

	def test_register_route_already_signed_in(self):
		result = self.client.get("/register")
		self.assertIn("Redirecting..", result.data)

	def test_login_already_signed_in(self):
		result = self.client.get("/login")
		self.assertIn("Redirecting..", result.data)

	def test_logout(self):
		# not sure how to test this either, since it primarily just deletes session key
		pass

	def test_compose_update_logged_in(self):
		pass

	def tearDown(self):
		db.session.close()
		db.drop_all()

class RouteTestCasesNoSession(unittest.TestCase):
	"""Tests flask route functions in server that don't use a session key or in fact require there to not be a session key"""

	def setUp(self):
		connect_to_db(app, "postgresql:///twitterclonetest")
		db.create_all()
		fake_test_data()
		self.client = s.app.test_client()
		s.app.config['TESTING'] = True
		s.app.config["SECRET_KEY"] = "masseffectrulez"

	def test_index_route(self):
		result = self.client.get("/")
		self.assertIn("<h1>My Feed</h1>", result.data)
		self.assertIn("Updates from All Users", result.data)
		self.assertIn("Updates from Your Connections", result.data)

	def test_register_route(self):
		result = self.client.get("/register")
		self.assertIn("Please enter a username (must be between 4 and 20 characters, \n\t\tonly contain valid characters without spaces, and be unique from \n\t\texisting users):", result.data)

	def test_register_success_route(self):
		result = self.client.post("/register-success", data={"username":"mordin", "password":"sciencelvr", "is_public":"1"})
		self.assertIsNotNone(User.query.filter(User.username == "mordin").first())

	def test_login_route(self):
		result = self.client.get("/login")
		self.assertIn("<h1>Log In</h1>", result.data)

	def test_login_success(self):
		result = self.client.post("/login-success", data={"username":"shepard", "password":"password123"})
		#find way to test? NEED TO ADDRESS

	def test_compose_update_not_logged_in(self):
		pass

	def tearDown(self):
		db.session.close()
		db.drop_all()

if __name__ == '__main__':
	unittest.main()