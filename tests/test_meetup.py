"""
Test the light wrapper around the Meetup.com API.

"""

from unittest import TestCase

import mock

from meetups.logic import meetup_get
from tests.utils import PatchMixin


class TestAPIWrapper(TestCase, PatchMixin):
    def setUp(self):
        self.uri = "test-uri"

    def test_uses_global_oauth_when_none_is_provided(self):
        meetup = self.patch("meetups.logic.meetup")
        meetup.get.return_value.data = {"meta" : {"next" : ""}, "results" : []}
        list(meetup_get(self.uri))
        self.assertTrue(meetup.get.called)

    def test_sets_charset_header(self):
        oauth = mock.NonCallableMock()
        oauth.get.return_value.data = {"meta" : {"next" : ""}, "results" : []}

        results = list(meetup_get(self.uri, oauth=oauth))
        args, kwargs = oauth.get.call_args
        self.assertEqual(kwargs["headers"]["Accept-Charset"], "utf-8")

    def test_returns_combined_results_from_all_pages(self):
        def get(endpoint, *args, **kwargs):
            data = {
                self.uri : {
                    "meta" : {"next" : "page-2"}, "results" : [{"id" : 1}],
                },
                "page-2" : {
                    "meta" : {"next" : "page-3"},
                    "results" : [{"id" : 2}, {"id" : 3}],
                },
                "page-3" : {
                    "meta" : {"next" : ""}, "results" : [],
                },
            }[endpoint]

            return mock.Mock(data=data)

        oauth = mock.NonCallableMock(**{"get.side_effect" : get})

        results = meetup_get(self.uri, oauth=oauth)
        expected_results = [{"id" : 1}, {"id" : 2}, {"id" : 3}]
        self.assertEqual(list(results), expected_results)
