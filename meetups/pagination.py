from math import ceil


class InvalidPage(Exception):
    pass


class Pagination(object):
    """An iterable class to provide paged results, based loosely on the one
    found at http://flask.pocoo.org/snippets/44/.
    """
    def __init__(self, items, page, limit):
        items = list(items)
        self.total = len(items)

        if page is None:
            page = 1
        if limit is None:
            limit = self.total

        self.limit = limit

        if page < 1 or page > self.pages:
            raise InvalidPage('page must be between 1 and %d.' % self.pages)

        offset = (page - 1) * limit
        self.items = items[offset:offset + limit]

        self.page = page
        self.count = min(limit, len(self.items))

    def __getitem__(self, k):
        return self.items[k]

    def __iter__(self):
        for item in self.items:
            yield item

    @property
    def has_next_page(self):
        """Returns ``True`` if there is a next page."""
        return self.page < self.pages

    @property
    def has_previous_page(self):
        """Returns ``True`` if there is a previous page."""
        return self.page > 1

    @property
    def pages(self):
        """Returns the total number of pages."""
        return int(ceil(self.total / float(self.limit)))
