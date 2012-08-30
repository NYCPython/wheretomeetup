from unittest import TestCase

import meetups
import mock

from meetups import logic
from tests.utils import PatchMixin


class TestUserSync(TestCase, PatchMixin):
    def setUp(self):
        self.meetup = self.patch("meetups.logic.meetup")
        self.meetup.get.return_value.data = {
            "meta" : {"next" : ""}, "results" : []
        }
        self.user = mock.NonCallableMock()

    def test_refreshes_if_needed(self):
        with meetups.app.test_request_context():
            logic.sync_user(self.user, maximum_staleness=100)
        self.user.refresh_if_needed.assert_called_once_with(100)

    def test_sets_the_location(self):
        lon, lat = self.user.lon, self.user.lat

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertEqual(self.user.loc, (lon, lat))

    def test_creates_group_models(self):
        groups = [{"id" : 1}, {"id" : 12}]
        member_of = [group["id"] for group in groups]
        self.patch("meetups.logic.meetup_get", return_value=iter(groups))
        Group = self.patch("meetups.logic.Group")

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        calls = [mock.call(_id=id) for id in member_of]
        self.assertEqual(calls, Group.call_args_list)
        self.assertEqual(len(Group.return_value.save.call_args_list), 2)

    def test_updates_the_groups(self):
        groups = [{"id" : 1}, {"id" : 12}]
        member_of = [group["id"] for group in groups]
        self.patch("meetups.logic.meetup_get", return_value=iter(groups))

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertEqual(self.user.member_of, member_of)

    def test_saves_the_user(self):
        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertTrue(self.user.save.called)
