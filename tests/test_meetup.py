"""
Test the light wrapper around the Meetup.com API.

"""

from unittest import TestCase

import mock

from meetups.meetup_api import Meetup, MeetupAPIError
from tests.utils import PatchMixin


class TestMeetupCore(TestCase, PatchMixin):
    def setUp(self):
        self.oauth = mock.NonCallableMock(get=mock.MagicMock())
        self.meetup = Meetup(self.oauth)

    def test_delegates_get_with_charset_to_oauth(self):
        self.meetup.get(1, foo=2)
        self.oauth.get.assert_called_once_with(
            1, foo=2, headers={"Accept-Charset" : "utf-8"},
        )

    def test_get_results_returns_results_from_all_pages(self):
        data_for_uris = {
            "test-uri" : {
                "meta" : {"next" : "page-2"}, "results" : [{"id" : 1}],
            },
            "page-2" : {
                "meta" : {"next" : "page-3"},
                "results" : [],
            },
            "page-3" : {
                "meta" : {"next" : ""}, "results" : [{"id" : 2}, {"id" : 3}],
            },
        }

        self.oauth.get.side_effect = (
            lambda e, *a, **kw : mock.Mock(data=data_for_uris[e])
        )

        results = list(self.meetup.get_results("test-uri"))
        self.assertEqual(results, [{"id" : 1}, {"id" : 2}, {"id" : 3}])

    def test_get_can_fail(self):
        data = self.oauth.get.return_value.data = {
            "problem" : "Big boom!",
            "details" : "The boom was big.",
            "other" : "thing",
        }
        with self.assertRaises(MeetupAPIError) as e:
            results = list(self.meetup.get(1))

        self.assertEqual(str(e.exception), data["problem"])
        self.assertIs(e.exception.error, data)


class TestMeetupWrapperMethods(TestCase, PatchMixin):
    def setUp(self):
        self.oauth = mock.NonCallableMock()
        self.meetup = Meetup(self.oauth)
        self.meetup.get_results = mock.Mock()

    def test_groups(self):
        groups = self.meetup.groups(
            member_id=1, fields=["thing", "other"], page=8,
        )

        self.assertEqual(groups, self.meetup.get_results.return_value)
        self.meetup.get_results.assert_called_once_with(
            self.meetup.ENDPOINTS["groups"],
            data=[("member_id", 1), ("fields", "thing,other"), ("page", 8)],
        )

    def test_venues(self):
        venues = self.meetup.venues(
            group_ids=[1, 2, 3], fields=["thing", "other"], page=8,
        )

        self.assertEqual(venues, self.meetup.get_results.return_value)
        self.meetup.get_results.assert_called_once_with(
            self.meetup.ENDPOINTS["venues"], data=[
                ("group_id", "1,2,3"),
                ("fields", "thing,other"),
                ("page", 8),
            ]
        )

    def test_events(self):
        events = self.meetup.events(
            group_ids=[1, 2, 3], status=["thing", "other"],
            fields=["field", "another"], page=8,
        )

        self.assertEqual(events, self.meetup.get_results.return_value)
        self.meetup.get_results.assert_called_once_with(
            self.meetup.ENDPOINTS["events"], data=[
                ("group_id", "1,2,3"),
                ("status", "thing,other"),
                ("fields", "field,another"),
                ("page", 8)
            ]
        )
