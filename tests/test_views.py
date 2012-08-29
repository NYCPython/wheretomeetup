from flask import Flask, url_for
from flask.ext.testing import TestCase

import mock

from meetups import app, views
from tests.utils import PatchMixin


class TestLoginSync(TestCase, PatchMixin):
    """
    The login sync view syncs a user with the Meetup API.

    """

    def setUp(self):
        self.client = self.app.test_client()
        self.member_id = 1

        with self.client.session_transaction() as session:
            session["member_id"] = self.member_id

        self.User = self.patch("meetups.views.User")
        self.login_user = self.patch("meetups.views.login_user")
        self.sync_user = self.patch("meetups.views.sync_user")

    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_syncs_a_loaded_user(self):
        user = self.User.with_id(self.member_id)
        self.client.get("/login/sync/")
        self.sync_user.assert_called_once_with(user)

    def test_logs_in_user(self):
        self.client.get("/login/sync/")
        self.assertTrue(self.login_user.called)

    def test_redirects_to_profile_after_sync(self):
        response = self.client.get("/login/sync/")
        self.assertRedirects(response, url_for("user_profile"))
