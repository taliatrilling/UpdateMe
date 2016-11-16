from server import app
import server as s 
from model import User, Update, Comment, Pair, Message, Request, connect_to_db, db, fake_test_data
import unittest
from flask_sqlalchemy import SQLAlchemy 
from flask import (Flask, render_template, redirect, request, session, flash, jsonify)
from passlib.hash import bcrypt


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
		self.assertEqual(s.add_connection_request(3, 4), 3)
		self.assertIsNotNone(Request.query.filter(Request.request_id == 3).first())

	def test_add_pair_to_db(self):
		self.assertEqual(s.add_pair_to_db(3, 4), 5)
		self.assertIsNotNone(Pair.query.filter(Pair.pair_id == 5).first())

	def test_get_connection_requests(self):
		requests = Request.query.filter(Request.requestee_id == 2).all()
		self.assertEqual(s.get_connection_requests(2), requests)

	def test_get_connection_requests_when_none(self):
		self.assertEqual(s.get_connection_requests(5), [])

	def test_usernames_behind_connection_requests(self):
		requests = Request.query.filter(Request.requestee_id == 2).all()
		self.assertEqual(s.usernames_behind_connection_requests(requests), ["liara"])

	def test_change_password(self):
		new_pass = "n7lady"
		user_id = 1
		s.change_password(user_id, new_pass)
		password_in_db = User.query.get(user_id).password
		verified = bcrypt.verify(new_pass, password_in_db)
		self.assertTrue(verified)

	def test_get_num_messages_between(self):
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
		result = self.client.get("/compose-update")
		self.assertIn("<h1>What's on your mind?</h1>", result.data)

	def test_update_posted_logged_in(self):
		result = self.client.post("/update-posted", data={"textbody": "Cmdr Shepard here!"})
		self.assertIsNotNone(Update.query.filter(Update.update_body == "Cmdr Shepard here!").first())

	def test_show_specific_update_owner_private_not_connected(self):
		result = self.client.get("/update/4")
		self.assertIn("Redirecting..", result.data)
		self.assertNotIn("I'm so going to betray Nihlus ;)", result.data)

	def test_show_specific_update_owner_private_connected(self):
		result = self.client.get("/update/1")
		self.assertIn("just in the middle of some calibrations", result.data)

	def test_add_comment_logged_in(self):
		result = self.client.post("/add-comment/1", data={"comment": "do you ever do anything else??"})
		self.assertIsNotNone(Comment.query.filter(Comment.comment_id == 4, Comment.update_id == 1).first())

	def test_show_inbox_logged_in(self):
		result = self.client.get("/inbox")
		self.assertIn("Conversation with garrus", result.data)

	def test_show_message_logged_in_in_pair(self):
		result = self.client.get("/message/1")
		self.assertIn("up for another contest on the citadel later?", result.data)
		self.assertIn("hell yes", result.data)

	def test_show_message_logged_in_not_in_pair(self):
		result = self.client.get("/message/4")
		self.assertIn("Redirecting..", result.data)
		self.assertNotIn("Would you like to start a conversation?", result.data)

	def test_compose_message_logged_in(self):
		result = self.client.get("/compose-message")
		self.assertIn("Message recipient:", result.data)

	def test_submit_message(self):
		result = self.client.post("/submit-message", data={"message": "dude your updates just make you look more suspicious", "chosen-recipient": 4})
		self.assertIsNotNone(Message.query.filter(Message.owner_id == 1, Message.recipient_id == 4).first())

	def test_submit_reply_message(self):
		result = self.client.post("/submit-reply-message", data={"message": "see you there tomorrow?", "recipient": 2})
		self.assertIsNotNone(Message.query.filter(Message.msg_id == 3).first())

	def test_view_own_profile(self):
		result = self.client.get("/profile/1")
		self.assertIn("Your Profile", result.data)

	def test_view_public_profile_connected(self):
		result = self.client.get("/profile/3")
		self.assertIn("You are currently connected with", result.data)

	def test_view_public_profile_not_connected(self):
		result = self.client.get("/profile/6")
		self.assertIn("you may still see their updates, but you may not message them", result.data)

	def test_view_private_profile_connected(self):
		result = self.client.get("/profile/2")
		self.assertIn("You are currently connected with", result.data)

	def test_view_private_profile_not_connected(self):
		result = self.client.get("/profile/5")
		self.assertNotIn("You are currently connected with", result.data)
		self.assertIn("you may request access below:", result.data)

	def test_feed_connects_json_route(self):
		pass
		#again, need guidance on ajax tests

	def test_request_connection_new(self):
		result = self.client.post("/request-connection/5")
		self.assertIsNotNone(Request.query.filter(Request.request_id == 3).first())
		self.assertIn("Redirecting..", result.data)

	def test_review_connection_requests_when_exist(self):
		result = self.client.get("/review-connection-requests")
		self.assertIn("has requested to connect", result.data)

	def test_approve_connection(self):
		result = self.client.get("/approve-connection/2")
		self.assertIsNotNone(Pair.query.filter(Pair.pair_id == 5).first())

	def test_change_password_success(self):
		result = self.client.post("/preferences/change-password-success", data={"current_password":"password123", "new_password":"n7lady"})
		password_in_db = User.query.get(1).password
		verified = bcrypt.verify("n7lady", password_in_db)
		self.assertTrue(verified)

	def tearDown(self):
		db.session.close()
		db.drop_all()

class RouteTestCasesSessionVersion2(unittest.TestCase):
	"""Tests flask route functions in server that rely on session keys but needed the user to have different user attributes
	than the previous set of test cases """

	def setUp(self):
		connect_to_db(app, "postgresql:///twitterclonetest")
		db.create_all()
		fake_test_data()
		self.client = s.app.test_client()
		s.app.config['TESTING'] = True
		s.app.config["SECRET_KEY"] = "masseffectrulez"
		with self.client as c:
			with c.session_transaction() as sess:
				sess["user_id"] = 6
				sess["username"] = "jenkins"

	def test_show_inbox_logged_in_no_messages(self):
		result = self.client.get("/inbox")
		self.assertNotIn("Conversation with", result.data)

	def test_compose_message_logged_in_no_connections(self):
		result = self.client.get("/compose-message")
		self.assertIn("You are not currently connected to any users!", result.data)

	def test_review_requests_none_exist(self):
		result = self.client.get("/review-connection-requests")
		self.assertIn("You have no current connection requests", result.data)

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
		result = self.client.get("/compose-update")
		self.assertIn("Redirecting..", result.data)

	def test_show_specific_update_owner_public(self):
		result = self.client.get("/update/2")
		self.assertIn("anyone want to open this bottle of serrice ice I got for Chakwas with me?", result.data)

	def test_show_specific_update_owner_private_not_logged_in(self):
		result = self.client.get("/update/4")
		self.assertIn("Redirecting..", result.data)
		self.assertNotIn("I'm so going to betray Nihlus ;)", result.data)

	def test_add_comment_not_logged_in(self):
		result = self.client.post("/add-comment/1")
		self.assertIn("Redirecting..", result.data)

	def test_show_inbox_not_logged_in(self):
		result = self.client.get("/inbox")
		self.assertIn("Redirecting..", result.data)

	def test_show_message_not_logged_in(self):
		result = self.client.get("/message/1")
		self.assertIn("Redirecting..", result.data)
		self.assertNotIn("up for another contest on the citadel later?", result.data)

	def test_compose_message_not_logged_in(self):
		result = self.client.get("/compose-message")
		self.assertIn("Redirecting..", result.data)

	# def test_check_username_for_ajax_does_exist(self):
	# 	result = self.client.get("/check-username", data={"username": "shepard"})
	# 	#check how to test ajax routes

	# def test_check_username_for_ajax_does_not_exist(self):
	# 	result = self.client.get("/check-username", data={"username": "shepardthesecond"})
		#check how to test ajax routes

	def test_feed_all_json(self):
		result = self.client.get("/feed-all-json")
		self.assertEqual('{\n  "results": [\n    [\n      "shepard", \n      "anyone want to open this bottle of serrice ice I got for Chakwas with me?", \n      "0:02 UTC on November 11, 2016", \n      1, \n      2\n    ]\n  ]\n}\n', result.data)

	def test_search_results(self):
		result = self.client.get("/search-results", query_string={"search":"shepard"})
		self.assertIn("Users with usernames matching your search:", result.data)
		self.assertIn("shepard", result.data)

	def test_view_profile_not_logged_in(self):
		result = self.client.get("/profile/1")
		self.assertIn("Redirecting..", result.data)
		self.assertNotIn("shepard", result.data)


	def tearDown(self):
		db.session.close()
		db.drop_all()

if __name__ == '__main__':
	unittest.main()