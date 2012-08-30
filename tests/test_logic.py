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
        self.user = mock.NonCallableMagicMock()

    def test_refreshes_if_needed(self):
        with meetups.app.test_request_context():
            logic.sync_user(self.user, maximum_staleness=100)
        self.user.refresh_if_needed.assert_called_once_with(100)

    def test_sets_the_location(self):
        lon, lat = self.user.lon, self.user.lat

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertEqual(self.user.loc, (lon, lat))

    def test_syncs_the_groups(self):
        sync_groups = self.patch("meetups.logic.sync_groups")
        meetup_get = self.patch("meetups.logic.meetup_get")

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        endpoint, = meetup_get.call_args[0]

        sync_groups.assert_called_once_with(self.user, meetup_get.return_value)
        self.assertTrue(endpoint.startswith(logic.MEETUP_ENDPOINTS["groups"]))

    def test_saves_the_user(self):
        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertTrue(self.user.save.called)


class TestSyncGroups(TestCase, PatchMixin):
    def setUp(self):
        self.Group = self.patch("meetups.logic.Group")
        self.user = mock.NonCallableMock()
        self.groups = [
            {"id" : 1},
            {"id" : 2, "self" : {"role" : "Organizer"}},
            {"id" : 3, "self" : {"role" : "Co-Organizer"}},
        ]

    def test_creates_group_models(self):
        member_of = [group["id"] for group in self.groups]
        logic.sync_groups(self.user, self.groups)
        calls = [mock.call(_id=id) for id in member_of]
        self.assertEqual(calls, self.Group.call_args_list)
        self.assertEqual(len(self.Group.return_value.save.call_args_list), 3)

    def test_updates_the_groups(self):
        member_of = [group["id"] for group in self.groups]
        logic.sync_groups(self.user, self.groups)
        self.assertEqual(self.user.member_of, member_of)

    def test_updates_the_organizer_field(self):
        logic.sync_groups(self.user, self.groups)
        self.assertEqual(self.user.organizer_of, [2, 3])
