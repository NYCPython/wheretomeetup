from unittest import TestCase

from collections import Iterable

from meetups import pagination


class TestPagination(TestCase):
    def setUp(self):
        self.items = range(1, 5)

    def test_has_next_page(self):
        page = limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertTrue(pager.has_next_page)

        page = 2
        limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertTrue(pager.has_next_page)

        page = 4
        limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertFalse(pager.has_next_page)

    def test_has_previous_page(self):
        page = limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertFalse(pager.has_previous_page)

        page = 2
        limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertTrue(pager.has_previous_page)

        page = 4
        limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertTrue(pager.has_previous_page)

    def test_indexing(self):
        page = 1
        limit = 4
        pager = pagination.Pagination(self.items, page, limit)

        self.assertEqual(pager[0], self.items[0])
        self.assertEqual(pager[1], self.items[1])
        self.assertEqual(pager[2], self.items[2])
        self.assertEqual(pager[3], self.items[3])

        self.assertRaises(IndexError, lambda: pager[4])

    def test_initialization(self):
        page = limit = 1
        pager = pagination.Pagination(self.items, page, limit)

        self.assertEqual(pager.page, page)
        self.assertEqual(pager.count, limit)
        self.assertEqual(pager.total, len(self.items))
        self.assertEqual(pager.items, [1])

        page = 2
        limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.items, [2])

        page = 2
        limit = 2
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.items, [3, 4])

        page = 2
        limit = 3
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.count, 1)
        self.assertEqual(pager.items, [4])

        page = 1
        limit = 10
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.count, len(self.items))
        self.assertEqual(pager.items, self.items)

        page = limit = None
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.count, len(self.items))
        self.assertEqual(pager.items, self.items)

    def test_invalid(self):
        page = 10
        limit = 1
        self.assertRaises(pagination.InvalidPage, pagination.Pagination,
                          self.items, page, limit)

        page = -1
        limit = 1
        self.assertRaises(pagination.InvalidPage, pagination.Pagination,
                          self.items, page, limit)

        page = 'a'
        limit = 1
        self.assertRaises(pagination.InvalidPage, pagination.Pagination,
                          self.items, page, limit)

        page = self.items
        limit = 1
        self.assertRaises(pagination.InvalidPage, pagination.Pagination,
                          self.items, page, limit)

    def test_iteration(self):
        page = 1
        limit = 4
        pager = pagination.Pagination(self.items, page, limit)
        self.assertTrue(isinstance(pager, Iterable))

    def test_pages(self):
        page = limit = 1
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.pages, len(self.items))

        page = 1
        limit = len(self.items)
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.pages, 1)

        page = 1
        limit = 2
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.pages, 2)

        page = 1
        limit = 3
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.pages, 2)

        page = 1
        limit = 5
        pager = pagination.Pagination(self.items, page, limit)
        self.assertEqual(pager.pages, 1)
