from unittest import TestCase

import meetups
import mock

from meetups import logic


class TestUserSync(TestCase):
    def setUp(self):
        self.user = mock.NonCallableMock()

        meetup_patch = mock.patch("meetups.logic.meetup")
        self.meetup = meetup_patch.start()
        self.addCleanup(meetup_patch.stop)

    def test_refreshes_if_needed(self):
        data = {"meta" : {"next" : ""}, "results" : []}
        self.meetup.get.return_value.data = data

        with meetups.app.test_request_context():
            logic.sync_user(self.user, maximum_staleness=100)
        self.user.refresh_if_needed.assert_called_once_with(100)

    def test_sets_the_location(self):
        data = {"meta" : {"next" : ""}, "results" : []}
        self.meetup.get.return_value.data = data
        lon, lat = self.user.lon, self.user.lat

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertEqual(self.user.loc, (lon, lat))

    def test_updates_with_the_groups_on_the_current_page(self):
        groups = [{"id" : 1}, {"id" : 12}]
        member_of = [group["id"] for group in groups]

        def get(endpoint, *args, **kwargs):
            if "groups" in endpoint:
                data = {"meta" : {"next" : ""}, "results" : groups}
            else:
                data = {"meta" : {"next" : ""}, "results" : []}
            return mock.MagicMock(data=data)

        self.meetup.get.side_effect = get

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertEqual(self.user.member_of, member_of)

    def test_saves_the_user(self):
        data = {"meta" : {"next" : ""}, "results" : []}
        self.meetup.get.return_value.data = data

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertTrue(self.user.save.called)
