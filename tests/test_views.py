from flask import Flask, url_for
from flask.ext.testing import TestCase

import mock

from meetups import app, views


class TestLoginSync(TestCase):
    """
    The login sync view syncs a user with the Meetup API.

    """

    def create_app(self):
        app.config["TESTING"] = True
        return app

    def test_syncs_a_loaded_user(self):
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["member_id"] = 1

            with mock.patch("meetups.views.User") as User:
                with mock.patch("meetups.views.sync_user") as sync_user:
                    with mock.patch("meetups.views.login_user") as login_user:
                        user = User.with_id(session["member_id"])
                        client.get("/login/sync/")

            sync_user.assert_called_once_with(user)

    def test_logs_in_user(self):
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["member_id"] = 1

            with mock.patch("meetups.views.User") as User:
                with mock.patch("meetups.views.sync_user") as sync_user:
                    with mock.patch("meetups.views.login_user") as login_user:
                        client.get("/login/sync/")

            self.assertTrue(login_user.called)

    def test_redirects_to_profile_after_sync(self):
        with self.app.test_client() as client:
            with client.session_transaction() as session:
                session["member_id"] = 1

            with mock.patch("meetups.views.User") as User:
                with mock.patch("meetups.views.sync_user") as sync_user:
                    with mock.patch("meetups.views.login_user") as login_user:
                        response = client.get("/login/sync/")

            self.assertRedirects(response, url_for("user_profile"))
