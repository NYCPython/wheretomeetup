from unittest import TestCase

import meetups
import mock

from meetups import logic
from tests.utils import PatchMixin


class TestUserSync(TestCase, PatchMixin):
    def setUp(self):
        self.meetup = self.patch("meetups.logic.meetup")
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

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        sync_groups.assert_called_once_with(
            self.user, self.meetup.groups.return_value
        )
        self.assertEqual(
            self.meetup.groups.call_args[1]["member_id"],
            self.user._id,
        )

    def test_saves_the_user(self):
        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        self.assertTrue(self.user.save.called)

    def test_creates_venues_with_taglists(self):
        create_venues = self.patch("meetups.logic.create_venues")

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        create_venues.assert_called_once_with(self.meetup.venues.return_value)
        self.assertEqual(
            self.meetup.venues.call_args[1]["group_ids"],
            self.user.member_of
        )
        self.assertIn("taglist", self.meetup.venues.call_args[1]["fields"])

    def test_creates_events(self):
        create_events = self.patch("meetups.logic.create_events")

        with meetups.app.test_request_context():
            logic.sync_user(self.user)

        create_events.assert_called_once_with(self.meetup.events.return_value)
        self.assertEqual(
            self.meetup.events.call_args[1]["group_ids"],
            self.user.member_of
        )


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


class TestCreatesVenues(TestCase, PatchMixin):
    def test_creates_venue_models(self):
        Venue = self.patch("meetups.logic.Venue")
        venues = [
            {"id" : 1, "lon" : 10, "lat" : 20},
            {"id" : 2, "lon" : 20, "lat" : 10}
        ]
        calls = [
            mock.call(_id=venue["id"], loc=(venue["lon"], venue["lat"]))
            for venue in venues
        ]

        logic.create_venues(venues)
        self.assertEqual(calls, Venue.call_args_list)
        self.assertEqual(len(Venue.return_value.save.call_args_list), 2)


class TestCreatesEvents(TestCase, PatchMixin):
    def test_creates_event_models(self):
        Event = self.patch("meetups.logic.Event")
        events = [
            {"id" : 1, "group" : {"id" : "3"}},
            {"id" : 2, "group" : {"id" : "4"}}
        ]
        calls = [
            mock.call(_id=event["id"], group_id=event["group"]["id"])
            for event in events
        ]

        logic.create_events(events)
        self.assertEqual(calls, Event.call_args_list)
        self.assertEqual(len(Event.return_value.save.call_args_list), 2)
