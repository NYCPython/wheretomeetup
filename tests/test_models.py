from unittest import TestCase

import mock

from meetups import models


class TestModel(TestCase):
    def test_fetch_by_id_gets_the_model(self):
        with mock.patch("meetups.models.Model.load") as load:
            m = models.Model.with_id(12)
            self.assertEqual(m._id, 12)

    def test_fetch_by_id_loads_the_model(self):
        with mock.patch("meetups.models.Model.load") as load:
            m = models.Model.with_id(12)
            load.assert_called_once_with()
