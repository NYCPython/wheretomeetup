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

from datetime import datetime

from flask import session
from flask.ext.login import LoginManager, UserMixin, AnonymousUser

from meetups import app, meetup, mongo

login_manager = LoginManager()


# Indexes
@app.before_first_request
def ensure_indexes():
    mongo.db[Venue.collection].ensure_index([('loc', '2d')])
    mongo.db[Venue.collection].ensure_index([('claimed', 1)])
    mongo.db[Venue.collection].ensure_index([('user_id', 1)])


@login_manager.user_loader
def load_user(id):
    user = User(_id=id).load()
    if getattr(user, '_id') == id:
        return user
    return None


class Model(object):
    """Base class for data models. Supports three modes of operation:

    1. :meth:`load` to retrieve (cached) data from MongoDB
    2. :meth:`refresh` to retrieve data from the Meetup API
    3. :meth:`save` to save data back to MongoDB

    Subclasses should override the :attr:`api_endpoint`, :attr:`collection`,
    and :attr:`api_identifer` class-level attributes with appropriate values.
    Subclasses should have a field (or property)

    Subclasses may override :attr:`dont_save_fields` with a sequence of
    field names that should not be saved to MongoDB.

    Subclasses may override :attr:`field_mapping` which maps field names
    from the Meetup API to names that will be used on object attributes
    and stored in MongoDB.
    """

    api_endpoint = None
    api_identifier = None
    collection = None
    field_mapping = {}
    dont_save_fields = []

    def __init__(self, **kwargs):
        self._map_fields(kwargs)

    @classmethod
    def with_id(cls, id):
        """
        Retrieve and load the model object with the id ``id``.

        """

        model = cls(_id=id)
        model.load()
        return model

    def load(self):
        """Return ``True`` if the document was found, or ``False`` otherwise.
        """
        #XXX This docstring lies.
        if not hasattr(self, '_id'):
            raise TypeError('Model subclasses must define an _id attribute')
        if self.collection is None:
            raise TypeError('Model subclasses must set a collection attribute')

        doc = mongo.db[self.collection].find_one(self._id) or {}
        for k, v in doc.iteritems():
            setattr(self, k, v)

        return self

    def refresh(self):
        if self.api_endpoint is None:
            raise TypeError('Model subclasses must set an api_endpoint attribute')
        if self.api_identifier is None:
            raise TypeError('Model subclasses must set an api_identifier attribute')

        url = self.api_endpoint % vars(self)
        response = meetup.get(url, headers={'Accept-Charset': 'utf-8'})
        data = getattr(response, 'data', {})
        self._map_fields(data)

    def refresh_if_needed(self, maximum_staleness):
        """Check the :attr:`modified` timestamp, and call :meth:`refresh` if
        it is older than the `maximum_staleness` (in seconds). Return ``True``
        if :meth:`refresh` was called, and ``False`` otherwise.
        """
        created = getattr(self, 'created', datetime(1970, 1, 1, 0, 0, 0))
        staleness = datetime.utcnow() - created
        if staleness.total_seconds() > maximum_staleness:
            self.refresh()
            return True
        return False

    def save(self):
        if not hasattr(self, '_id'):
            raise TypeError('Model subclasses must define an _id attribute')
        if self.collection is None:
            raise TypeError('Model subclasses must set a collection attribute')

        doc = {}
        for k, v in vars(self).iteritems():
            if k in ('api_endpoint', 'api_identifier', 'collection', 'dont_save_fields'):
                continue
            if k in self.dont_save_fields:
                continue
            doc[k] = v

        now = datetime.utcnow()
        if 'created' not in doc:
            doc['created'] = now
        doc['modified'] = now

        _id = doc.pop('_id')
        mongo.db[self.collection].update({'_id': _id}, {'$set': doc}, upsert=True)

    def _map_fields(self, fields):
        for k, v in fields.iteritems():
            k = self.field_mapping.get(k, k)
            setattr(self, k, v)


class User(Model, UserMixin):
    api_endpoint = '/2/member/%(_id)s'
    api_identifier = '_id'
    field_mapping = {
        'id': '_id'
    }
    collection = 'users'

    def __unicode__(self):
        return self.name

    def get_id(self):
        """Make this model compatible with expectations of Flask-Login.
        """
        return self._id

    def update_profile(self, email, phone):
        mongo.db[self.collection].update({'_id': self._id},
            {'$set': {'email': email, 'phone': phone}})
        self.load()


class Group(Model):
    api_endpoint = '/2/groups/?group_id=%(_id)s'
    api_identifier = '_id'
    field_mapping = {
        'id': '_id'
    }
    collection = 'groups'


class Guest(AnonymousUser):
    # define name to be compatible with :class:`User`
    name = 'Guest'
login_manager.anonymous_user = Guest


class Venue(Model):
    field_mapping = {'id': '_id'}
    collection = 'venues'
    dont_save_fields = ['distance']

    def __unicode__(self):
        return self.name

    def claim(self, user_id, **fields):
        """Mark a venue as claimed, adding any additional information as well.

        In order to claim the venue, the `user_id` must be provided. All other
        fields will be passed through the keyword args (`**fields`). The name
        of the keyword argument will be mapped to the keys of the document
        with the following exceptions:

         * `contact_name` will be stored as `contact.name`
         * `contact_email` will be stored as `contact.email`
         * `contact_phone` will be stored as `contact.phone`
        """

        self.claimed = True
        self.user_id = user_id

        contact = getattr(self, 'contact', {})
        if 'contact_name' in fields:
            contact['name'] = fields.pop('contact_name')
        if 'contact_email' in fields:
            contact['email'] = fields.pop('contact_email')
        if 'contact_phone' in fields:
            contact['phone'] = fields.pop('contact_phone')
        self.contact = contact

        for field in fields:
            setattr(self, field, fields.get(field))

        self.save()


class Event(Model):
    field_mapping = {'id': '_id'}
    collection = 'events'
    dont_save_fields = []
