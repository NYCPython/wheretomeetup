from unittest import TestCase

import mock

from meetups import models
from tests.utils import PatchMixin


class TestModel(TestCase, PatchMixin):
    def setUp(self):
        self.load = self.patch("meetups.models.Model.load")

    def test_fetch_by_id_gets_the_model(self):
        m = models.Model.with_id(12)
        self.assertEqual(m._id, 12)

    def test_fetch_by_id_loads_the_model(self):
        m = models.Model.with_id(12)
        self.load.assert_called_once_with()
