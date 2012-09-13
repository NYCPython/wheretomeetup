# Copyright (c) 2012, The NYC Python Meetup
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
