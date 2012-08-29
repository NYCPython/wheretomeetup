from unittest import TestCase

import meetups
import mock

from meetups import logic


class TestUserSync(TestCase):
    def test_it_refreshes_if_needed(self):
        with mock.patch("meetups.logic.User.load") as load:
            with mock.patch("meetups.logic.meetup") as oauth_client:
                member_id = 1
                user = load.return_value
                data = {"meta" : {"next" : ""}, "results" : []}
                oauth_client.get.return_value.data = data

                with meetups.app.test_request_context():
                    logic.sync_user(member_id, maximum_staleness=100)
                user.refresh_if_needed.assert_called_once_with(100)

    def test_it_sets_the_location(self):
        with mock.patch("meetups.logic.User.load") as load:
            with mock.patch("meetups.logic.meetup") as oauth_client:
                member_id = 1
                user = load.return_value
                data = {"meta" : {"next" : ""}, "results" : []}
                oauth_client.get.return_value.data = data
                lon, lat = user.lon, user.lat

                with meetups.app.test_request_context():
                    logic.sync_user(member_id)

                self.assertEqual(user.loc, (lon, lat))

    def test_it_updates_with_the_groups_on_the_current_page(self):
        with mock.patch("meetups.logic.User.load") as load:
            with mock.patch("meetups.logic.meetup") as oauth_client:
                member_id = 1
                user = load.return_value
                groups = [{"id" : 1}, {"id" : 12}]
                member_of = [group["id"] for group in groups]

                def get(endpoint, *args, **kwargs):
                    if "groups" in endpoint:
                        data = {"meta" : {"next" : ""}, "results" : groups}
                    else:
                        data = {"meta" : {"next" : ""}, "results" : []}
                    return mock.MagicMock(data=data)

                oauth_client.get.side_effect = get

                with meetups.app.test_request_context():
                    logic.sync_user(member_id)

                self.assertEqual(user.member_of, member_of)

    def test_it_saves_the_user(self):
        with mock.patch("meetups.logic.User.load") as load:
            with mock.patch("meetups.logic.meetup") as oauth_client:
                member_id = 1
                user = load.return_value
                data = {"meta" : {"next" : ""}, "results" : []}
                oauth_client.get.return_value.data = data

                with meetups.app.test_request_context():
                    logic.sync_user(member_id)

                self.assertTrue(user.save.called)
